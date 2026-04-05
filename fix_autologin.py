#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sessionStorage -> localStorage로 변경하여 자동 로그인 유지"""
import os

fp = r'C:\xampp\htdocs\mysite\msk-library-temp\index.html'
with open(fp, 'r', encoding='utf-8') as f:
    content = f.read()

count = content.count("sessionStorage")
content = content.replace("sessionStorage", "localStorage")
new_count = content.count("localStorage.getItem('msk_auth')")

with open(fp, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'[OK] sessionStorage -> localStorage: {count} replacements')
print(f'File size: {os.path.getsize(fp):,} bytes')
