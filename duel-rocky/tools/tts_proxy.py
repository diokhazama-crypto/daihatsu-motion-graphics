"""Run core/tts/tts_zh.py with edge-tts trusting the CA bundle in SSL_CERT_FILE (needed behind a TLS-terminating proxy).
Usage: python tools/tts_proxy.py <LIB>/core/tts/tts_zh.py lines.json out_dir"""
import os, sys, runpy, certifi
ca = os.environ.get('SSL_CERT_FILE')
if ca and os.path.exists(ca): certifi.where = lambda: ca
script = sys.argv[1]; sys.argv = sys.argv[1:]
runpy.run_path(script, run_name='__main__')
