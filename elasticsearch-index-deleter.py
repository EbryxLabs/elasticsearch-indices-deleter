import os
import json
import argparse
from pprint import pprint
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch


args = ''
default_vars_dict = {
        'out_log': '{0}-out.log'.format(os.path.realpath(__file__)),
        'config_file': 'config.json',
        'indices_deleted': []
    }


def setup_argparse():
    global args
    argparse_setup_completed_gracefully = False
    parser = argparse.ArgumentParser(
        description='''Set this script up as a cron job. It shall delete all indices that as per params defined in config''',
        epilog="""All's well that ends well.""",
        usage="""python3 {0}.py --config""".format(str(__file__)))
    parser.add_argument('--out_log', '-o', '-O', '-OUTPUT',
        default=default_vars_dict['out_log'],
        required=False,
        help='path/to/name/of/output/log/file'
    )
    parser.add_argument('--config', '-c', '-C', '-CONFIG',
        default=default_vars_dict['config_file'],
        required=False,
        help='path/to/name/of/config/file'
    )
    parser.add_argument('--testing', '-tg',
        help='Won\'t actually delete indices. Just displays indices that would\'ve be deleted',
        action='store_true'
    )
    args = parser.parse_args()


def log_msg(msg):
    with open(args.out_log, 'a') as o:
        msg = '{0} === {1}'.format(datetime.now(), str(msg))
        o.write('{0}\n'.format(msg))
        print(msg)


def index_older_than_defined_days(es, index, max_age_in_days):
    index_is_older_than_defined_number_of_days = False
    log_msg('Reading settings for index {0}'.format(index))
    res = es.indices.get_settings(index=index)
    log_msg('Index creation date {0}'.format(res[index]['settings']['index']['creation_date']))
    index_creation_date = datetime.utcfromtimestamp(float(res[index]['settings']['index']['creation_date'])/1000)
    log_msg('Index {0} was created on {1}'.format(index, index_creation_date.strftime('%Y-%m-%dT%H:%M:%SZ')))
    log_msg('Timedelta calculated for index {0} is {1}'.format(index, index_creation_date + timedelta(days=max_age_in_days), datetime.utcnow()))
    if index_creation_date + timedelta(days=max_age_in_days) <= datetime.utcnow():
        index_is_older_than_defined_number_of_days = True
    log_msg('Index {0} deletion = {1}'.format(index, index_is_older_than_defined_number_of_days))
    return index_is_older_than_defined_number_of_days


def index_matches_naming_pattern(index, indices_pattern_to_be_deleted):
    is_set_for_deletion = False
    if True in (delete_pattern in index for delete_pattern in indices_pattern_to_be_deleted):
        is_set_for_deletion = True
    log_msg('Index name {0} matches pattern for deletion = {1}'.format(index, is_set_for_deletion))
    return is_set_for_deletion


def load_config(path_to_config):
    log_msg('Loading config from path {0}'.format(path_to_config))
    with open(path_to_config) as json_file:
        data = json.load(json_file)
        log_msg('Config loaded successfully from path {0}'.format(path_to_config))
        print('Data loaded from config is as follows:')
        pprint(data)
        return data


def main():
    global args
    args.config = load_config(args.config)
    es = Elasticsearch(hosts=[{'host': args.config['ES_IP'], 'port': args.config['ES_PORT']}])

    # get all indices
    indices = es.indices.get("*")
    # deletion logic
    for index in indices:
        log_msg('Starting checks for index {0}'.format(index))
        if index_matches_naming_pattern(index, [index_name for index_name, max_age_in_days in args.config['indices_to_delete'].items()]):
            for index_name, max_age_in_days in args.config['indices_to_delete'].items():
                if index_name in index and index_older_than_defined_days(es, index, args.config['indices_to_delete'][index_name]):
                    if not args.testing:
                        res = es.indices.delete(index=index, ignore=[400, 404])
                        log_msg('Index {0} has been deleted'.format(index))
                    default_vars_dict['indices_deleted'].append(index)
    print('Following indices deleted:')
    pprint(default_vars_dict['indices_deleted'])


if __name__ == '__main__':
    setup_argparse()
    log_msg('Log parser setup completed')

    mTime = [datetime.now(), 0]
    log_msg('Start Time: {0}'.format(mTime[0]))

    main()

    mTime[1] = datetime.now()
    log_msg('End Time: {0}'.format(mTime[1]))
    log_msg('Time Diff: {0}'.format(mTime[1] - mTime[0]))