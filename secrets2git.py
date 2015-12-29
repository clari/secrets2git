# -*- coding: utf-8 -*-

print('secrets2git: starting')

import boto3
import os
from cryptography.fernet import Fernet
import imp
import sys
import subprocess

CONF_FILE_NAME = 'Secrets2GitConf.py'
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/'
conf = imp.load_source('conf', PARENT_DIR + CONF_FILE_NAME)
EXTENSION = '.encrypted'


def say(message):
    print('secrets2git: ' + message)

try:
    client = boto3.client('kms', region_name=conf.REGION_NAME)
except:
    if not conf.AWS_ACCESS_KEY_ID:
        say('AWS_ACCESS_KEY_ID must be set in your environment')
        exit(1)

    if not conf.AWS_SECRET_ACCESS_KEY:
        say('AWS_SECRET_ACCESS_KEY must be set in your environment')
        exit(1)

    client = boto3.client('kms', region_name=conf.REGION_NAME,
                          aws_access_key_id=conf.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=conf.AWS_SECRET_ACCESS_KEY)

if 'KEY' not in dir(conf):
    say('secrets2git key not found in ' + CONF_FILE_NAME)
    say('Do you want to create a new one?')
    answer = raw_input()
    if 'y' in answer:
        key = Fernet.generate_key()
        response = client.encrypt(
            KeyId=conf.KMS_KEY_ID,
            Plaintext=key)
        encoded = response['CiphertextBlob'].encode('base64')
        say('')
        say('Add the following to ' + CONF_FILE_NAME + ' -----------')
        say('')
        say('KEY = """' + encoded + '"""')
        say('')
    else:
        exit(1)
elif conf.KMS_KEY_ID is None:
    say('KMS key id not set in ' + CONF_FILE_NAME)
    exit(1)

fernet_key = client.decrypt(
    CiphertextBlob=conf.KEY.decode('base64'))['Plaintext']

fernet = Fernet(fernet_key.encode('ascii'))

if len(sys.argv) < 2:
    say('pass decrypt or encrypt as first argument')
    exit(1)


def decrypt(filename):
    with open(PARENT_DIR + filename + EXTENSION, 'r') as in_file:
        contents = ''.join(in_file.readlines()[1:])  # Skip header
        decrypted = fernet.decrypt(contents.decode('base64'))
    return decrypted


def commit_encrypted_files(file_names):
    if file_names:
        say('The following secret files were changed:')
        for file_name in file_names:
            say('\t' + file_name)
        say('Please enter a commit message for your change:')
        commit_message = raw_input()
        say('committing')
        cmd = 'git commit %s -am "%s"' % (' '.join(file_names), commit_message)
        say(cmd)
        subprocess.call(cmd)

encrypted_file_names = []
if sys.argv[1] == 'encrypt':
    for file_name in conf.FILES_TO_ENCRYPT:
        if not os.path.isfile(file_name):
            say(file_name + ' does not exist, skipping')
            continue
        with open(PARENT_DIR + file_name, 'rb') as in_file:
            contents = in_file.read()
            if contents != decrypt(file_name):
                header = 'Encrypted with secrets2git'.ljust(76, '-') + '\n'
                encrypted = header + fernet.encrypt(contents).encode('base64')
                say('Encrypting ' + file_name)
                with open(PARENT_DIR + file_name + EXTENSION, 'w') as out_file:
                    out_file.write(encrypted)
                encrypted_file_names.append(file_name + EXTENSION)
    if not encrypted_file_names:
        say('No secrets changed')
    if os.environ.get('SECRETS2GIT_COMMIT', None):
        commit_encrypted_files(encrypted_file_names)
    elif encrypted_file_names:
        say('Please commit:')
        for file_name in encrypted_file_names:
            say('\t' + file_name)
elif sys.argv[1] == 'decrypt':
    for file_name in conf.FILES_TO_ENCRYPT:
        say('decrypting ' + file_name)
        decrypted = decrypt(file_name)
        with open(PARENT_DIR + file_name, 'w') as out_file:
            out_file.write(decrypted)
else:
    say('invalid first argument, must be decrypt or encrypt')

