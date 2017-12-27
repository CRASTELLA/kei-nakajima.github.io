# -*- coding:utf-8
"""
gen-pages.py
replace pages in mkdocs.yml with contents in document folder
"""
import sys
import getopt
import os
import glob
import frontmatter
import ruamel.yaml
from ruamel.yaml.scalarstring import SingleQuotedScalarString, DoubleQuotedScalarString
from collections import OrderedDict
import codecs
import shutil

def ruamel_represent_odict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', dict(instance))

ruamel.yaml.representer.RoundTripRepresenter.add_representer(
    OrderedDict,
    ruamel_represent_odict)

def gen_page_od(path, dirname):
    name = os.path.basename(path)
    post = frontmatter.load(path)
    if 'title' in list(post.keys()):
        title_sq = SingleQuotedScalarString(post['title'])
        value_sq = SingleQuotedScalarString(dirname + name)
        od = OrderedDict()
        od[title_sq] = value_sq
        return od
    else:
        return SingleQuotedScalarString(dirname + name)

def gen_pages_od(path, dirname):
    ret = []
    files = glob.glob(os.path.join(path, '*'))
    for f in files:
        if os.path.isdir(f):
            name = os.path.basename(f)
            if not name.startswith('_'):
                name_sq = SingleQuotedScalarString(name)
                od = OrderedDict()
                od[name_sq] = gen_pages_od(f, dirname + name + '/')
                ret.append(od)
        else:
            ret.append(gen_page_od(f, dirname))
    return ret

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts,args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error as msg:
        print (msg)
        print ("for help use --help")
        return 2

    for o,a in opts:
        if o in ("-h","--help"):
            print (__doc__)
            return 0

    filename = 'mkdocs.yml'
    if not os.path.exists(filename):
        print ('error: not found file (mkdocs.yml)')
        return 0

    backup_filename = 'mkdocs.yml.bak'
    if os.path.exists(backup_filename):
        os.remove(backup_filename)

    filename = 'mkdocs.yml'
    shutil.copy2(filename, backup_filename)

    f = open('mkdocs.yml')
    data = ruamel.yaml.round_trip_load(f, preserve_quotes=True)
    f.close()

    pages = None;
    if len(args) == 0:
        pages = gen_pages_od('./docs/', '')
    else:
        pages = []
        for a in args:
            path = './docs/' + a
            if os.path.isdir(path):
                name_sq = SingleQuotedScalarString(a)
                od = OrderedDict()
                od[name_sq] = gen_pages_od(path, a + '/')
                pages.append(od)
            else:
                pages.append(gen_page_od(path, ''))

    f = codecs.open(filename, 'w+', 'utf-8')
    data['pages'] = pages
    f.write(ruamel.yaml.round_trip_dump(data, default_flow_style=False, encoding='utf-8', allow_unicode=True, explicit_start=False))
    f.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())
