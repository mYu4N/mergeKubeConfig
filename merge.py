#!/usr/bin/env python
# encoding: utf-8
# Author: guoxudong yufeng.s muyuan.y
import argparse
import json
import os

import yaml

FLAGS = None

KUBECONFIG = {
    "kind": "Config",
    "apiVersion": "v1",
    "preferences": {},
    "clusters": [],
    "users": [],
    "contexts": [],
    "current-context": ""
}

ALLCONTEXTS = []


class ToException(Exception):
    def __init__(self, err='请选择源配置文件'):
        Exception.__init__(self, err)


class AddException(Exception):
    def __init__(self, err='请选择配置文件'):
        Exception.__init__(self, err)


def getLocalDirectory():
    """
    Process local directory
    获取目录地址
    :param dir:
    :return: 配置文件目录路径
    """
    return os.path.dirname(os.path.realpath(__file__)) + '/' + FLAGS.directory + '/'


def getLocalFile(filename):
    """
    Process local files
    获取文件地址
    :param dir:
    :return: 配置文件路径
    """
    return os.path.dirname(os.path.realpath(__file__)) + '/' + filename


def addConfig():
    """
    增加配置文件
    :return:
    """
    add_path = getLocalFile(FLAGS.add)
    to_path = getLocalFile(FLAGS.to)
    handleAddConfig(add_path, to_path)


def loadYamlFile(path):
    """
    读取yaml文件
    :param path:
    :return:
    """
    with open(path, 'r') as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)


def handleAddConfig(addfile, oldconfig):
    """
    处理增加配置
    :return:
    """
    add_config = loadYamlFile(addfile)
    to_config = loadYamlFile(oldconfig)
    add_content = handleYaml(add_config, FLAGS.add.split('/')[-1])
    to_config['clusters'].extend(add_content.get('clusters', ''))
    to_config['users'].extend(add_content.get('users', ''))
    to_config['contexts'].extend(add_content.get('contexts', ''))
    KUBECONFIG['clusters'] = to_config['clusters']
    KUBECONFIG['users'] = to_config['users']
    KUBECONFIG['contexts'] = to_config['contexts']


def readFiles(curPath):
    """
    读取文件
    :return:
    """
    fileList = os.listdir(curPath)
    for filename in fileList:
        handleConfig(curPath + filename, filename)


def handleYaml(c, filename):
    """
    处理yaml
    :param content:  yaml内容
    :param filename: 文件名称
    :return:
    """
    for i, context in enumerate(c.get('contexts', '')):
        cluster = context['context']['cluster']
        user = context['context']['user']
        _ctt_name_list = context['name'].split('-')
        name = filename + '-' + str(i)
        context['name'] = name
        ALLCONTEXTS.append(name)

        for clu in c.get('clusters', ''):
            if cluster == clu['name']:
                # cluster_name = name + '-cluster'
                cluster_name = _ctt_name_list[1]
                clu['name'] = cluster_name
                context['context']['cluster'] = cluster_name

        if len(c.get('clusters')) > len(c.get('users')):
            # user_name = name + '-user'
            user_name = name + '-' + _ctt_name_list[0]
            c['users'][0]['name'] = user_name
            context['context']['user'] = user_name
        else:
            for usr in c.get('users', ''):
                if user == usr['name']:
                    # user_name = name + '-user'
                    user_name = name + '-' + _ctt_name_list[0]
                    usr['name'] = user_name
                    context['context']['user'] = user_name

    return c


def handleConfig(path, filename):
    """
    处理配置
    :param path: 配置文件路径
    :return:
    """
    with open(path, 'r') as f:
        all = yaml.load(f.read(), Loader=yaml.FullLoader)
        result = handleYaml(all, filename)
        KUBECONFIG['clusters'].extend(result.get('clusters', ''))
        KUBECONFIG['users'].extend(result.get('users', ''))
        KUBECONFIG['contexts'].extend(result.get('contexts', ''))


def outputFile():
    """
    输出文件
    :return:
    """
    with open('config', 'w') as f:
        f.write(json.dumps(KUBECONFIG))


def main():
    """
    主方法
    :return:
    """
    if FLAGS.add != '' and FLAGS.to == '':
        raise ToException
    elif FLAGS.add == '' and FLAGS.to != '':
        raise AddException
    elif FLAGS.add != '' and FLAGS.to != '':
        addConfig()
        print('开始')
    else:
        readFiles(getLocalDirectory())
    outputFile()
    print('# COPY configfile to .kube:')
    print('cp config ~/.kube\n')
    print('# View all users:')
    print('kubectl config get-contexts\n')
    print('# learn more:')
    print('kubectl config --help\n')
    print('# Cluster switching command:')
    for command in ALLCONTEXTS:
        print('kubectl config use-context {0}'.format(command))
    # print(ALLCONTEXTS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        dest="directory",
        default="configfile",
        type=str,
        help="the directory kubeconfig!")
    parser.add_argument(
        "-t",
        "--to",
        dest="to",
        default="",
        type=str,
        help="the kubeconfig that need to join the configured file!")
    parser.add_argument(
        "-a",
        "--add",
        dest="add",
        default="",
        type=str,
        help="add new config to kubeconfig!")
    FLAGS, unparsed = parser.parse_known_args()
    main()
