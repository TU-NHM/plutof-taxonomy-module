#!/usr/bin/python
import sys
import argparse
import csv
import json
import time
import requests

parser = argparse.ArgumentParser(description="Script to upload data from csv formatted file into taxonomy module.")
parser.add_argument("infile", help="csv formatted file, see docs for the exact format")
parser.add_argument("-t", "--tree", help="tree_id", type=int)
parser.add_argument("-r", "--rank_type", help="rank_type", type=int)
parser.add_argument("-b", "--base_url", help="base url, e.g. http://localhost:7000/api/ or https://api.example.com/", required=True)
parser.add_argument("-a", "--auth_url", help="oauth2 url, e.g. http://localhost:7000/oauth2/access_token/ or https://api.example.com/oauth2/access_token/", required=True)
args = parser.parse_args()

# open files to print errors and tab-separated list of correct taxa
f = open("csv_error.log", "w")
m = open("csv_main.txt", "w")

if args.rank_type == 1:
    rank_dict = {"1": "10", "2": "20", "3": "23", "4": "28", "5": "30", "6": "33", "7": "38",
                 "8": "40", "9": "43", "10": "48", "11": "50", "12": "53", "13": "55",
                 "14": "60", "15": "63", "16": "65", "17": "70", "18": "73", "19": "74",
                 "20": "76", "21": "100", "22": "90", "25": "34", "27": "67", "28": "67",
                 "29": "44", "30": "35", "31": "36", "32": "84", "33": "47", "35": "13",
                 "37": "14", "38": "18", "39": "24", "41": "37", "44": "56", "49": "69",
                 "50": "72"}
elif args.rank_type == 2:
    rank_dict = {"kingdom": "10", "phylum": "20", "subphylum": "23", "superclass": "28",
                 "class": "30", "subclass": "33", "superorder": "38", "order": "40",
                 "suborder": "43", "superfamily": "48", "family": "50", "subfamily": "53",
                 "tribe": "55", "genus": "60", "subgenus": "63", "section": "65",
                 "species": "70", "subspecies": "73", "variety": "74", "form": "76",
                 "hybrid": "100", "cultivar": "90", "infraclass": "34", "group_genus": "67",
                 "infraorder": "44", "division": "35", "subdivision": "36", "morph": "84",
                 "subkingdom": "13", "infrakingdom": "14", "superphylum": "18",
                 "infraphylum": "24", "infradivision": "37", "subtribe": "56",
                 "aggregate": "69", "microspecies": "72", "section": "47"}
else:
    rank_dict = {"10": "10", "20": "20", "23": "23", "28": "28", "30": "30", "33": "33",
                 "38": "38", "40": "40", "43": "43", "48": "48", "50": "50", "53": "53",
                 "55": "55", "60": "60", "63": "63", "65": "65", "70": "70", "73": "73",
                 "74": "74", "76": "76", "100": "100", "90": "90", "34": "34", "67": "67",
                 "44": "44", "35": "35", "36": "36", "84": "84", "13": "13", "14": "14",
                 "18": "18", "24": "24", "37": "37", "56": "56", "69": "69", "72": "72",
                 "47": "47"}

""" Add to PlutoF:
14 - Infrakingdom/present,
24 - Infraphylum/present,
(33) 47 - Organism group, Section/present,
(27,28) 67 - Group (Genus)/present
"""

# create dicts to hold new db id-s and urls to refer back to parent_id-s
taxonomy_id_dict = {}
taxonomy_url_dict = {}

# record count
count = 0
err = 0

# start counting runtime
time_start_total = time.time()
time_start_part = time.time()

# settings
base_url = args.base_url
url_oauth2 = args.auth_url
client_id = "4908fdadf35697117048"
client_secret = "299191c8d310a3d818ac16f8f103711a3e968e14"
uname = "admin"
pwd = "pass"

# authorize
print "Authenticating..."
oauth2_headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
oauth2_payload = {"client_id": client_id,
                  "client_secret": client_secret,
                  "grant_type": "password",
                  "username": uname,
                  "password": pwd,
                  "scope": "write"}
r = requests.post(url_oauth2, data=oauth2_payload, headers=oauth2_headers)
if r.status_code != 200:
    f.write(r.url + "\n" + str(r.status_code) + ": " + r.text + "\n")
    f.write(json.dumps(oauth2_payload))
    r.raise_for_status()
    sys.exit()

json_data = r.json()
access_token = json_data["access_token"]
token_type = json_data["token_type"]
token = token_type + " " + access_token

print "Got the token, will proceed now. Will report after each 500 updates."

# prepare headers with access token
url_headers = {"Authorization": token}
url_headers_json = {"Authorization": token, "Content-type": "application/json"}

# POST new tree
if args.tree is None:
    url_post_tree = base_url + "taxonomy/tree/"
    meta_payload = {"name": "New tree"}
    r = requests.post(url_post_tree, data=json.dumps(meta_payload), headers=url_headers_json)
    if r.status_code != 201:
        f.write(r.url + "\n" + str(r.status_code) + ": " + r.text + "\n")
        f.write(json.dumps(meta_payload))
        f.write("Cannot add new tree\n")
        sys.exit()
    json_data = r.json()
    new_tree_id = json_data["id"]
    new_tree_url = json_data["url"]
    print "New tree added with id " + str(new_tree_id)
else:
    new_tree_id = args.tree
    new_tree_url = base_url + "taxonomy/tree/" + str(args.tree) + "/"
    print "Using existing tree to add taxon nodes - " + new_tree_url


# POST taxon node data
with open(args.infile) as source:
    dataReader = csv.reader(source, delimiter="\t")
    for row in dataReader:
        # taxon_id [0]
        # parent_taxon_id [1]
        # taxon_rank_id [2]
        # epithet [3]
        # author [4]
        # year [5]
        # code [6]
        # vernacular names [7]
        # use parentheses [8]
        count += 1
        meta_payload = None
        use_parentheses = "False"
        if count > 1:
            if row[0] in taxonomy_id_dict:
                # taxon already added, skip the duplicate
                err += 1
                f.write("ERR: Taxon already processed - " + str(row[0]) + "\n")
            elif int(row[1]) == int(0):
                # add first level taxon (incl. taxa with parent node missing)
                tmp_taxon_rank = base_url + "taxonomy/taxon_rank/" + str(rank_dict[row[2]]) + "/"
                if row[8] and int(row[8]) == 1:
                    use_parentheses = "True"
                meta_payload = {"format": "json",
                                "epithet": str(row[3]),
                                "tree": new_tree_url,
                                "epithet_author": str(row[4]),
                                "year_described_in": str(row[5]),
                                "use_parentheses": use_parentheses,
                                "taxon_rank": tmp_taxon_rank,
                                "code": str(row[6])
                                }
                f.write("ERR: First level taxon - " + str(row[0]) + "\n")
            elif not row[1] in taxonomy_url_dict:
                err += 1
                f.write("ERR: Parent missing for  - " + str(row[0]) + "\n")
            else:
                # parent is present
                tmp_taxon_rank = base_url + "taxonomy/taxon_rank/" + str(rank_dict[row[2]]) + "/"
                if row[8] and int(row[8]) == 1:
                    use_parentheses = "True"
                meta_payload = {"format": "json",
                                "epithet": str(row[3]),
                                "tree": new_tree_url,
                                "epithet_author": str(row[4]),
                                "year_described_in": str(row[5]),
                                "use_parentheses": use_parentheses,
                                "taxon_rank": tmp_taxon_rank,
                                "code": str(row[6]),
                                "parent": str(taxonomy_url_dict[row[1]])
                                }
            if meta_payload:
                url_post_taxonnode = base_url + "taxonomy/taxon/"
                r = requests.post(url_post_taxonnode, data=json.dumps(meta_payload), headers=url_headers_json)
                if r.status_code != 201:
                    f.write(r.url + "\n" + str(r.status_code) + ": " + r.text + "\n")
                    f.write(json.dumps(meta_payload))
                    f.write("Cannot add new taxonnode - " + row[0] + "\n")
                    sys.exit()
                json_data = r.json()
                new_id = json_data["id"]
                new_url = json_data["url"]
                taxonomy_id_dict[row[0]] = new_id
                taxonomy_url_dict[row[0]] = new_url
                # write mapping to main file
                m.write(str(row[0]) + "\t" + str(new_id) + "\n")

                # check if there are vernacular names to be added
                if row[7]:
                    cn_list = row[7].split(";")
                    for cn in cn_list:
                        tmp_cn = cn.split(":")
                        if tmp_cn[1]:
                            url_post_commonname = base_url + "taxonomy/vernacular_name/"
                            tmp_lang_url = base_url + "taxonomy/language/" + tmp_cn[1] + "/"
                            meta_payload = {"common_name": str(tmp_cn[0]),
                                            "iso_639": tmp_lang_url,
                                            "taxon_node": new_url
                                            }
                            r = requests.post(url_post_commonname, data=json.dumps(meta_payload), headers=url_headers_json)
                            if r.status_code != 201:
                                f.write(r.url + "\n" + str(r.status_code) + ": " + r.text + "\n")
                                f.write(json.dumps(meta_payload))
                                f.write("Cannot add new vernacular name - " + row[0] + "\n")

            # display process status
            if (count % 500) == 0:
                time_end_part = time.time()
                print "%d taxon nodes done! - time taken: %.2f seconds" % (count, time_end_part - time_start_part)
                time_start_part = time.time()
f.close()
m.close()

# print out the number of correct taxa about to be added to db
total_count = count - err - 1
print "\nTotal number of taxa: " + str(total_count)

# end here and print out runtime
print "Everything seemed to work smoothly, will stop here."
time_end_total = time.time()
print "Total time taken: %.2f seconds" % (time_end_total - time_start_total)
