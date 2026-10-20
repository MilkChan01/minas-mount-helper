#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 瘦客户端（runtime owner）：只经受保护 Unix socket 发命令、读脱敏 status。

- 不持有发现/发布/自愈线程；GUI 关闭仅断开连接，不停止服务。
- 不直连后端、不传任意上游目标/凭证；凭证永不经过客户端。
"""
import json
import os
import socket


class IpcClient:
    def __init__(self, socket_path, timeout=10):
        self.socket_path = socket_path
        self.timeout = timeout
        self._sock = None
        self._reader = None
        self._seq = 0

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc):
        self.close()

    def connect(self):
        if not os.path.exists(self.socket_path):
            raise FileNotFoundError(f"服务 socket 不存在：{self.socket_path}")
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.settimeout(self.timeout)
        self._sock.connect(self.socket_path)
        self._reader = self._sock.makefile("r", encoding="utf-8")

    def call(self, cmd, args=None):
        self._seq += 1
        payload = {"cmd": cmd, "id": self._seq, "args": args or {}}
        self._sock.sendall(
            (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
        if self._reader is None:
            self._reader = self._sock.makefile("r", encoding="utf-8")
        line = self._reader.readline()
        if not line:
            raise ConnectionError("服务无响应")
        resp = json.loads(line)
        if not resp.get("ok"):
            raise RuntimeError(resp.get("error") or "命令失败")
        return resp.get("data") or {}

    def status(self):
        return self.call("status")

    def close(self):
        if self._reader is not None:
            try:
                self._reader.close()
            except OSError:
                pass
            self._reader = None
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
