#!/usr/bin/env python
from PIL import Image
import os
import shutil
import re
from multiprocessing import Process
import functools
from parallel import MultiConsumer, MultiProducer

MX_WIDTH = 1024
staticPath = os.path.join("..", "static_assets")
digestPath = staticPath.replace("static_assets", "static")
renderFiles = [
    os.path.join(digestPath, "css", "roselia.css"),
    os.path.join(digestPath, "js", "utils.js")
]

class ScanIMG(MultiProducer):
    def task_put(self):
        for p, _, f in os.walk(digestPath):
            if len(f): print('  |> In dir:', p)
            for tf in f:
                self.add_task((tf, p))

class CompressIMG(MultiConsumer):
    def execute(self, task):
        tf, p = task
        postfix = tf.split('.')[-1]
        PIC_COMP = ['jpg', 'jpeg', 'png']
        if postfix.lower() in PIC_COMP:
            dep = len(p.split(os.pathsep)) + 1
            print('  '*dep, '|>', tf)
            path = os.path.join(p, tf)
            im = Image.open(path)
            w, h = im.size
            if w > MX_WIDTH:
                h = h * MX_WIDTH // w
                w = MX_WIDTH
            print('  '*(dep+1), "=> {} * {}".format(w, h))
            im = im.resize((w, h), Image.ANTIALIAS)
            im.save(path)
if __name__ == '__main__':
    print("Start building assets...")

    print("Step#1 creating & copying dir:", staticPath, '=>', digestPath)
    if os.path.exists(digestPath):
        print("  previous version found, removing...")
        shutil.rmtree(digestPath)
    shutil.copytree(staticPath, digestPath)
    
    print("Step#2 compressing images...")
    scanner = ScanIMG(CompressIMG)
    scanner.start()
    print("Step#4 compressing javascripts...")
    os.system("node build-assets.js -s {} -d {}".format(digestPath, digestPath))
    scanner.join()
    print("Finished!")