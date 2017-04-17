# -*- coding: utf-8 -*-

print('secrets2git: Starting')

import boto3
import botocore.session
import os
from cryptography.fernet import Fernet
import imp
import sys
import subprocess
import os.path
from os.path import expanduser

CONF_FILE_NAME = 'Secrets2GitConf.py'
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/'
CONF_FILE_PATH = PARENT_DIR + CONF_FILE_NAME
if os.path.isfile(os.path.join(CONF_FILE_PATH)):
    conf = imp.load_source('conf', CONF_FILE_PATH)
else:
    print('Please configure {CONF_FILE_NAME} in the root directory of your project with:\n'
          '`cp secrets2git/Secrets2GitConf.sample.py Secrets2GitConf.py`\n'
          'and then setting the variables appropriately in Secrets2GitConf.py'
          .format(CONF_FILE_NAME=CONF_FILE_NAME))
    exit(1)
EXTENSION = '.encrypted'
HOME = expanduser("~")

def say(message):
    print('secrets2git: ' + message)

def get_client():

    session = botocore.session.get_session()
    AWS_ACCESS_KEY_ID = session.get_credentials().access_key
    AWS_SECRET_ACCESS_KEY = session.get_credentials().secret_key

    if not (AWS_ACCESS_KEY_ID is None):
        if not (AWS_SECRET_ACCESS_KEY is None):
            return boto3.client('kms', region_name=conf.REGION_NAME,
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    say('value not found in session')

    if os.path.isfile(HOME + '/.aws/credentials'):
        return boto3.client('kms', region_name=conf.REGION_NAME)
    else:
        if not conf.AWS_ACCESS_KEY_ID:
            return False
        elif not conf.AWS_SECRET_ACCESS_KEY:
            return False
        else:
            return boto3.client('kms', region_name=conf.REGION_NAME,
                          aws_access_key_id=conf.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=conf.AWS_SECRET_ACCESS_KEY)


def encrypt_files(fernet):
    encrypted_file_names = []
    for file_name in conf.FILES_TO_ENCRYPT:
        file_path = PARENT_DIR + file_name
        file_path_encrypted = file_path + EXTENSION
        if not os.path.isfile(file_name):
            say(file_name + ' does not exist, skipping')
            continue
        encrypt(encrypted_file_names, fernet, file_name, file_path,
                file_path_encrypted)
    if not encrypted_file_names:
        say('No secrets changed')
    if os.environ.get('SECRETS2GIT_COMMIT', None):
        commit_encrypted_files(encrypted_file_names)
    elif encrypted_file_names:
        say('Please add and commit:')
        for file_name in encrypted_file_names:
            say('\t' + file_name)


def encrypt(encrypted_file_names, fernet, file_name, file_path,
            file_path_encrypted):
    with open(file_path, 'rb') as in_file:
        contents = in_file.read()
        is_first_encryption = not os.path.isfile(file_path_encrypted)
        if is_first_encryption or contents != decrypt(file_name, fernet):
            header = 'Encrypted with secrets2git'.ljust(76, '-') + '\n'
            encrypted = header + fernet.encrypt(contents).encode('base64')
            with open(file_path_encrypted, 'w') as out_file:
                out_file.write(encrypted)
            encrypted_file_names.append(file_name + EXTENSION)
            say('Encrypted ' + file_name)


def decrypt_files(fernet):
    for file_name in conf.FILES_TO_ENCRYPT:
        decrypted = decrypt(file_name, fernet)
        with open(PARENT_DIR + file_name, 'w') as out_file:
            out_file.write(decrypted)
        say('Decrypted ' + file_name)

def decrypt_file(file_name, fernet):
    decrypted = decrypt(file_name, fernet)
    with open(PARENT_DIR + file_name, 'w') as out_file:
        out_file.write(decrypted)
        say('Decrypted ' + file_name)


def decrypt(filename, fernet):
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


def ensure_key(client):
    if 'KEY' not in dir(conf):
        say('secrets2git key not found in ' + CONF_FILE_NAME)
        answer = raw_input('Do you want to create a new one (y, n)? ')
        if 'y' in answer:
            generate_key(client)
        exit(1)
    elif conf.KMS_KEY_ID is None:
        say('KMS key id not set in ' + CONF_FILE_NAME)
        exit(1)


def generate_key(client):
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


def main():
    client = get_client()
    if not client:
        say('AWS credentials not found in ~/.aws/credentials or in '
            'AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables')
        exit(1)
    ensure_key(client)
    fernet_key = client.decrypt(
        CiphertextBlob=conf.KEY.decode('base64'))['Plaintext']
    fernet = Fernet(fernet_key.encode('ascii'))
    if len(sys.argv) < 2:
        say('pass decrypt or encrypt as first argument')
        exit(1)

    if len(sys.argv) >= 3:
        if sys.argv[1] == 'decrypt':
            decrypt_file(sys.argv[2], fernet)
        else:
            say('invalid option for first argument, only decrypt supported when filename is passed')
    else:
        if sys.argv[1] == 'encrypt':
            encrypt_files(fernet)
        elif sys.argv[1] == 'decrypt':
            decrypt_files(fernet)
        else:
            say('invalid first argument, must be decrypt or encrypt')

if __name__ == '__main__':
    main()
