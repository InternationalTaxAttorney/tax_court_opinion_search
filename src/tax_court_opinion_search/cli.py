import argparse

from tax_court_opinion_search.download import download_data


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('download-data')

    args = parser.parse_args()

    if args.command == 'download-data':
        data_dir = download_data()
        print(f'Data downloaded to: {data_dir}')
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
