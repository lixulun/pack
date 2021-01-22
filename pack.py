import os, os.path
import pathlib
import logging, logging.config
import re
from zipfile import ZipFile
from datetime import date

"""
打包项目文件，使用正则指定排除规则
"""

targetDir = "pack"
excludePatterns = [
    targetDir + r'/.*\.zip$', # 排除打包目标文件
]

regxPatterns = [re.compile(p) for p in excludePatterns]

logging.basicConfig(format="[%(asctime)s][%(levelname)s] %(message)s", level=logging.DEBUG)
debug = logging.debug
info = logging.info

def rotateFileName(filename):
    """
    给路径名加后缀加后缀
    """
    if not os.path.exists(filename):
        return filename
    ityger = 2
    while True:
        fn = os.path.basename(filename)
        path = os.path.dirname(filename)
        name, extend = fn.rsplit('.', 1)
        fn = f"{name}-{ityger}.{extend}"
        ityger += 1
        if not os.path.exists(pathlib.Path(path)/fn):
            break
    return pathlib.Path(path)/fn

def walkDir(path):
    """
    递归列出指定 path 下的所有文件
    """
    try:
        os.listdir(path)
    except PermissionError:
        logging.warning("Permission error with '%s' dir, skipped.", path)
        return

    for p in os.listdir(path):
        new_path = os.path.join(path, p)
        if os.path.isdir(new_path):
            yield from walkDir(new_path)
        else:
            yield str(pathlib.Path(new_path)).replace("\\", "/")

def matchFileQ(file):
    return any(True if regx.match(file) else False for regx in regxPatterns)

def expandPattern(patterns):
    matches = []
    for pat in patterns:
        matches.extend(pathlib.Path().glob(pat))
    debug(matches)
    return matches

if not os.path.exists(targetDir):
    os.mkdir(targetDir)

write2 = rotateFileName(f"{targetDir}/pack{date.today().isoformat()}.zip")
with ZipFile(write2, mode='w') as zf:
    for realFile in filter(lambda x: not matchFileQ(x), walkDir('./')):
        debug("found file: " + realFile)
        info(f"Writing {realFile}...")
        zf.write(realFile, realFile)
        info(f"Writed {realFile}.")
    info(f"Done '{write2}'")
