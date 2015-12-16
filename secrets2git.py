# -*- coding: utf-8 -*-

print('secrets2git: starting')

import boto3
import os
from cryptography.fernet import Fernet
import imp
import sys

CONF_FILE_NAME = 'Secrets2GitConf.py'
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/'
conf = imp.load_source('conf', PARENT_DIR + CONF_FILE_NAME)
EXTENSION = '.encrypted'

client = boto3.client('kms', region_name=conf.REGION_NAME,
                      aws_access_key_id=conf.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=conf.AWS_SECRET_ACCESS_KEY)

if 'KEY' not in dir(conf):
    print('secrets2git key not found in ' + CONF_FILE_NAME)
    print('Do you want to create a new one?')
    answer = raw_input()
    if 'y' in answer:
        key = Fernet.generate_key()
        response = client.encrypt(
            KeyId=conf.KMS_KEY_ID,
            Plaintext=key)
        encoded = response['CiphertextBlob'].encode('base64')
        print('')
        print('Add the following to ' + CONF_FILE_NAME + ' -----------')
        print('')
        print('KEY = """' + encoded + '"""')
        print('')
    else:
        exit(1)
elif conf.KMS_KEY_ID is None:
    print('KMS key id not set in ' + CONF_FILE_NAME)
    exit(1)

fernet_key = client.decrypt(
    CiphertextBlob=conf.KEY.decode('base64'))['Plaintext']

fernet = Fernet(fernet_key.encode('ascii'))

if len(sys.argv) < 2:
    print('pass decrypt or encrypt as first argument')
    exit(1)


def decrypt(filename):
    with open(PARENT_DIR + filename + EXTENSION, 'r') as in_file:
        contents = ''.join(in_file.readlines()[1:])  # Skip header
        decrypted = fernet.decrypt(contents.decode('base64'))
    return decrypted

if sys.argv[1] == 'encrypt':
    for filename in conf.FILES_TO_ENCRYPT:
        if not os.path.isfile(filename):
            print('secrets2git: ' + filename + ' does not exist, skipping')
            continue
        with open(PARENT_DIR + filename, 'rb') as in_file:
            contents = in_file.read()
            if contents != decrypt(filename):
                header = 'Encrypted with secrets2git'.ljust(76, '-') + '\n'
                encrypted = header + fernet.encrypt(contents).encode('base64')
                print('secrets2git:' + filename + ' changed, encrypting...')
                with open(PARENT_DIR + filename + EXTENSION, 'w') as out_file:
                    out_file.write(encrypted)
elif sys.argv[1] == 'decrypt':
    for filename in conf.FILES_TO_ENCRYPT:
        print('secrets2git: decrypting ' + filename)
        decrypted = decrypt(filename)
        with open(PARENT_DIR + filename, 'w') as out_file:
            out_file.write(decrypted)
else:
    print('invalid first argument, must be decrypt or encrypt')

print('secrets2git: finished')
# TODO: Git submodule update --init
# TODO: Tries to install secrets2git dependencies
# TODO: '' decrypts this file and stores it here on git pull - in dev and cloud
# TODO: '' encrypts this file and checks it in on git push
# TODO: Deploy does git submodule update --init like clarius_web

# this file from mc ~/.dev-secrets/clarius_core/branch where branch defaults to master
