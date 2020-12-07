import time

import pytest
import requests

from conftest import create_application, upload_file


class TestAPI:
    @pytest.fixture(scope='class')
    def _application(self, aws_bucket):
        with create_application(aws_bucket) as procs:
            yield procs

    def test_index_page_has_github_link(self, _application):
        resp = requests.get('http://localhost:8080/')
        assert 'https://github.com/uktrade/trade-tariff-api/' in resp.text

    def test_invalid_date_on_taricdeltas_400s(self, _application):
        resp = requests.get('http://localhost:8080/api/v1/taricdeltas/not-a-date')
        assert resp.status_code == 400

    def test_valid_date_with_no_data_on_taricdeltas_404s(self, _application):
        resp = requests.get('http://localhost:8080/api/v1/taricdeltas/1990-01-01')
        assert resp.status_code == 404

    def test_invalid_file_sequence_id_for_taricfile_400s(self, _application):
        resp = requests.get(
            'http://localhost:8080/api/v1/taricdeltas/not-a-6-digit-number'
        )
        assert resp.status_code == 400

    def test_valid_sequence_id_with_no_file_on_taricfiles_404s(self, _application):
        resp = requests.get('http://localhost:8080/api/v1/taricfiles/999999')
        assert resp.status_code == 404

    def test_valid_present_sequence_id_on_taricfiles_200s(
        self, _application, aws_s3_client, aws_bucket
    ):
        upload_file(
            aws_s3_client,
            aws_bucket,
            key='taricfiles/200000.xml',
            target='tests/valid.xml',
        )
        resp = requests.get('http://localhost:8080/api/v1/taricfiles/200000')
        assert resp.status_code == 200

    def test_api_key_required_for_upload_endpoint(self, _application):
        pass

    def test_whitelisted_ip_required_for_upload_endpoint(self, _application):
        pass


class TestAPISentry:
    @pytest.fixture(scope='class')
    def _application(self, aws_bucket):
        with create_application(
            aws_bucket, env={'SENTRY_DSN': 'http://foo@localhost:9001/1'}
        ) as procs:
            yield procs

    def test_sentry(self, _application):
        pass


class TestAPIGoogleAnalytics:
    @pytest.fixture(scope='class')
    def _application(self, aws_bucket):
        with create_application(
            aws_bucket,
            env={
                'GA_ENDPOINT': 'http://localhost:9002',
                'GA_TRACKING_ID': 'UA-000000-1',
            },
        ) as procs:
            yield procs

    def test_server_side_google_analytics(self, _application):
        resp = requests.get('http://localhost:8080/')
        print(resp.text)
        time.sleep(1)
        resp = requests.post('http://localhost:9002/calls')
        assert resp.text == '1'


class TestAPIElasticAPM:
    @pytest.fixture(scope='class')
    def _application(self, aws_bucket):
        with create_application(
            aws_bucket,
            env={
                'ELASTIC_APM_URL': 'http://localhost:9003',
                'ELASTIC_APM_TOKEN': 'secret_token',
            },
        ) as procs:
            yield procs

    def test_elastic_apm(self, _application):
        pass
