# -*- coding: utf-8 -*-

import boto3
import os
from cryptography.fernet import Fernet
import imp

CONF_FILE_NAME = 'Secrets2GitConf.py'
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/'
conf = imp.load_source('conf', PARENT_DIR + CONF_FILE_NAME)

client = boto3.client('kms', region_name=conf.REGION_NAME,
                      aws_access_key_id=conf.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=conf.AWS_SECRET_ACCESS_KEY)

if 'KEY' not in dir(conf):
    print('Secrets2Git key not found in ' + CONF_FILE_NAME)
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
        print('Please get the encrypted key from a fellow developer')
    exit(1)
elif conf.KMS_KEY_ID is None:
    print('KMS key id not set in ' + CONF_FILE_NAME)
    exit(1)

fernet_key = client.decrypt(
    CiphertextBlob=conf.KEY.decode('base64'))['Plaintext']

fernet = Fernet(fernet_key.encode('ascii'))

for filename in conf.FILES_TO_ENCRYPT:
    with open(PARENT_DIR + filename, 'rb') as in_file:
        contents = in_file.read()
        encrypted = fernet.encrypt(contents).encode('base64')
        with open(PARENT_DIR + filename + '.encrypted', 'w') as out_file:
            out_file.write(encrypted)
    pass


# TODO: '' decrypts this file and stores it here on git pull - in dev and cloud
# TODO: '' encrypts this file and checks it in on git push

# this file from mc ~/.dev-secrets/clarius_core/branch where branch defaults to master
