from __future__ import print_function
import os
from glob import glob
from collections import namedtuple
from sql_to_readme import sql_to_readme
from utility import asset_dir
from utility import top_dir
from utility import this_dir
from utility import filter_lists


Appendix = namedtuple('Appendix', ['link', 'name', 'content'])

def update_local_readmes():
    for fl in filter_lists:
        sql_path = os.path.join(this_dir, "sql", "{}.sql".format(fl.sql))
        sql = open(sql_path).read()
        # Create a readme file based on the query
        readme_txt = sql_to_readme(sql)
        readme_path = os.path.join(asset_dir, fl.path, 'README.md')
        with open(readme_path, 'w') as f:
            f.write('\n[comment]: # (DO NOT EDIT; GENERATED FILE)\n\n')
            f.write(readme_txt)


def update_joint_readme():
    top = os.path.join(asset_dir, "GFW")
    doc = []
    appendices = []

    base = os.path.dirname(top)
    last_level = -1
    doc.append('\n[comment]: # (DO NOT EDIT; GENERATED FILE)\n')
    doc.append('# Treniformis')
    doc.append('<a name="contents">')
    doc.append('## Contents')
    doc.append('</a>')
    for linkno, (root, dirs, files) in enumerate(os.walk(top)):
        dirs[:] = sorted(x for x in dirs if not x.startswith('.'))
        data_files = sorted(x for x in files if not (x.startswith('.') or x.lower().startswith('readme')))
        readmes = sorted(x for x in files if x.lower().startswith('readme'))
        if len(readmes) > 1:
            raise RuntimeError('multiple README files in ' + top)
        link = 'link-{}'.format(linkno)
        relpath = os.path.relpath(root, base)
        name = os.path.basename(root)
        level = relpath.count('/')
        indent = '    ' * level
        if readmes:
            doc.append('{indent}* [{name}](#{link})'.format(indent=indent, name=name, link=link))
        else:
            doc.append('{indent}* {name}'.format(indent=indent, name=name))
        for dfile in data_files:
            dname = os.path.splitext(dfile)[0]
            doc.append('{indent}    - {dname}'.format(indent=indent, dname=dname))
        if readmes:
            readme_path = os.path.join(root, readmes[0])
            with open(readme_path) as f:
                readme = f.read()
        else:
            readme = None
        appendices.append(Appendix(link, relpath, readme))

    doc.append('')
    doc.append('---------')
    doc.append('## READMEs')    

    for apdx in appendices:
        if apdx.content:
            doc.append('')
            doc.append('<a name="{link}"></a>'.format(link=apdx.link))
            doc.append('### {} [[toc]](#contents)'.format(apdx.name))
            doc.append('')
            for line in apdx.content.strip().split('\n'):
                if line.startswith('#'):
                    line = '###' + line
                doc.append(line)

            doc.append('')
            doc.append('--------')
    doc = doc[:-1] # remove final hrule

    result = '\n'.join(doc)
    with open(os.path.join(top_dir, "CONTENTS.md"), 'w') as f:
        f.write(result)


def update_readmes():
    update_local_readmes()
    update_joint_readme()


if __name__ == '__main__':
    update_readmes()

