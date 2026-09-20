"""Diagnose Windows test-directory locks without changing the tested source."""
import ctypes, json, os, sys, tempfile, unittest
from ctypes import wintypes
from pathlib import Path
E=Path('WORKSPACE/extras/der-evidence/vs2-draft-repair/r1')
class Entry(ctypes.Structure):
 _fields_=[('obj',ctypes.c_void_p),('pid',ctypes.c_size_t),('handle',ctypes.c_size_t),('access',wintypes.ULONG),('trace',wintypes.USHORT),('kind',wintypes.USHORT),('attributes',wintypes.ULONG),('reserved',wintypes.ULONG)]
nt=ctypes.WinDLL('ntdll');k=ctypes.WinDLL('kernel32',use_last_error=True)
k.GetFileType.argtypes=[wintypes.HANDLE];k.GetFileType.restype=wintypes.DWORD
k.GetFinalPathNameByHandleW.argtypes=[wintypes.HANDLE,wintypes.LPWSTR,wintypes.DWORD,wintypes.DWORD];k.GetFinalPathNameByHandleW.restype=wintypes.DWORD

def handles():
 size=1024*1024
 while True:
  buf=ctypes.create_string_buffer(size);needed=wintypes.ULONG()
  result=nt.NtQuerySystemInformation(64,buf,size,ctypes.byref(needed))
  if result==0:break
  if size>128*1024*1024:return [{'error':'handle inventory too large'}]
  size=max(size*2,needed.value+65536)
 count=ctypes.c_size_t.from_buffer(buf).value;rows=[]
 for index in range(count):
  entry=Entry.from_buffer(buf,16+index*ctypes.sizeof(Entry))
  if entry.pid!=os.getpid() or k.GetFileType(entry.handle)!=1:continue
  path=ctypes.create_unicode_buffer(32768)
  if k.GetFinalPathNameByHandleW(entry.handle,path,32768,0) and 'der-tmp' in path.value:
   rows.append({'handle':entry.handle,'path':path.value,'access':entry.access})
 return rows
original=tempfile.TemporaryDirectory.cleanup

def cleanup(self):
 try:return original(self)
 except PermissionError as error:
  record={'temporary_directory':self.name,'error':str(error),'pid':os.getpid(),'cwd':os.getcwd(),'own_handles':handles()}
  (E/'cleanup-lock-diagnostic.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
  print(json.dumps(record),file=sys.stderr);raise

tempfile.TemporaryDirectory.cleanup=cleanup
sys.path.insert(0, 'tests')
import test_study_cli
suite=unittest.TestSuite(test_study_cli.RegistrationTest('test_changed_or_untracked_implementation_cannot_claim_registered_code') for _ in range(40))
result=unittest.TextTestRunner(verbosity=2,failfast=True).run(suite)
raise SystemExit(not result.wasSuccessful())
