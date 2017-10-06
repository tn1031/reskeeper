# -*- coding: utf-8 -*-

import json
import os
import tarfile
import shutil
import slackweb
import yaml

from google.cloud import storage


class ResKeeper():
    def __init__(self, config_path):
        self.config = yaml.load(open(config_path))
        gcs_client = storage.Client.from_service_account_json(
                self.config['gcp-key-file'],
                project=self.config['gcp-project'])
        self.bucket = gcs_client.get_bucket(self.config['gcp-bucket'])
        self.slack = slackweb.Slack(url=self.config['slack-channel-hooks'])

    def run(self, out):
        out_tar = out + '.tar.gz'
        archive = tarfile.open(out_tar, mode='w:gz')
        archive.add(out)
        archive.close()

        dst = os.path.join(self.config['dst'], os.path.basename(out_tar))
        blob = self.bucket.blob(dst)
        blob.upload_from_filename(out_tar)

        attachment = {'title': '実験が終わりました',
                'color': 'good'}
        params_file = os.path.join(out, self.config['experiment-settings'])
        print(params_file)
        if os.path.isfile(params_file):
            params = json.load(open(params_file))
            if 'comment' in params:
                attachment['text'] = params['comment']
                params.pop('comment')
            fields = list()
            for k, v in params.items():
                fields.append({'title': k, 'value': v})
            attachment['fields'] = fields
        self.slack.notify(channel=self.config['slack-channel'],
                attachments=[attachment])

        os.remove(out_tar)
        if self.config['remove']:
            shutil.rmtree(out)
        
