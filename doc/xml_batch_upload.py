#!/usr/bin/python
import sys
import argparse
import httplib
import urllib
import json
import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

rank_dict = {'1': '10', '2': '20', '3': '23', '4': '28', '5': '30', '6': '33',
             '7': '38', '8': '40', '9': '43', '10': '48', '11': '50',
             '12': '53', '13': '55', '14': '60', '15': '63', '16': '65',
             '17': '70', '18': '73', '19': '74', '20': '76', '21': '100',
             '22': '90', '25': '34', '27': '67', '28': '67', '29': '44',
             '30': '35', '31': '36', '32': '84', '33': '57', '35': '13',
             '37': '14', '38': '18', '39': '24', '41': '37', '44': '56',
             '49': '69', '50': '72'}

""" Add to PlutoF: 14 - Infrakingdom/present, 24 - Infraphylum/present,
(33) - Organism group/skip for now, (27,28) 67 - Group (Genus)/present
"""

parser = argparse.ArgumentParser(description="Script to upload data from dyntaxa specific xml formatted file into taxonomy module.")
parser.add_argument("infile", help="xml formatted file, see docs for the exact format")
parser.add_argument("-t", "--tree", help="tree_id", type=int)
args = parser.parse_args()

# start counting runtime
time_start_total = time.time()

# open files to print errors and tab-separated list of correct taxa
f = open('ET_error.log', 'w')
m = open('ET_main.txt', 'w')


# define function to fetch info about children
def get_children(children_obj, parent_id, parent_rank):
    global count
    global err
    for child in children_obj:
        count += 1
        # print child
        child_taxon_info = child[2]
        child_taxon_id = child_taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}Id').text.encode('utf-8')
        child_taxon_name = child_taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}ScientificName').text.encode('utf-8')
        child_taxon_name = child_taxon_name.strip()
        child_taxon_author = child_taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}Author').text
        if child_taxon_author is None:
            child_taxon_author = ""
        else:
            child_taxon_author = child_taxon_author.encode('utf-8')
        child_taxon_author = child_taxon_author.strip()
        child_taxon_category = child_taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}CategoryId').text.encode('utf-8')
        child_taxon_is_valid = child_taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}IsValid').text.encode('utf-8')
        child_common_name = child_taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}CommonName').text
        if child_common_name is None:
            child_common_name = ""
        else:
            child_common_name = child_common_name.encode('utf-8')
        child_common_name = child_common_name.strip()

        if child_taxon_id in unique_dict:
            err += 1
            f.write("ERR: Taxon with this id (" + str(child_taxon_id) + ") has already been processed.\n")
        else:
            if int(child_taxon_category) == int("33") or int(child_taxon_category) == int("27") or int(child_taxon_category) == int("28"):
                err += 1
                f.write("ERR: Taxon rank not allowed (" + str(child_taxon_id) + ", " + child_taxon_category + ", " + child_taxon_name + ").\n")
            elif parent_rank >= rank_dict[child_taxon_category]:
                err += 1
                f.write("ERR: Parent taxon rank has to be lower than child taxon rank (" + str(child_taxon_id) + ").\n")
            else:
                unique_dict[child_taxon_id] = "1"
                if int(rank_dict[child_taxon_category]) >= int("70"):
                    child_taxon_name = child_taxon_name.replace("  ", " ")
                    temp_taxon_parts = child_taxon_name.split(" ", 2)
                    child_taxon_name = temp_taxon_parts[1]
                    if child_taxon_name == "":
                        err += 1
                        f.write("ERR: Taxon name (split) is empty (" + str(child_taxon_id) + ").\n")
                        exit()
                unique_dict[taxon_id] = "1"
                ids_dict[count] = child_taxon_id
                name_dict[count] = child_taxon_name
                author_dict[count] = child_taxon_author
                category_dict[count] = child_taxon_category
                # if parent is below sp level, use gen level taxon as parent
                if int(rank_dict[child_taxon_category]) > int("70"):
                    parent_rank = rank_dict[category_dict[parent_id]]
                    if parent_rank >= "70":
                        new_parent_id = parent_dict[parent_id]
                        new_parent_rank = rank_dict[category_dict[new_parent_id]]
                        if new_parent_rank >= "70":
                            print "ERR: too deep on the tree (" + str(child_taxon_id) + ").\n"
                            exit()
                        else:
                            parent_dict[count] = new_parent_id
                    else:
                        parent_dict[count] = parent_id
                else:
                    parent_dict[count] = parent_id
                valid_dict[count] = child_taxon_is_valid
                common_name_dict[count] = child_common_name
                if child[1] is not None:
                    get_children(child[1], count, rank_dict[child_taxon_category])

# read in the tree
tree = ET.parse(args.infile)

# record count
count = 0
err = 0

# create python dictionaries to store taxon info
ids_dict = {}
name_dict = {}
author_dict = {}
category_dict = {}
parent_dict = {}
valid_dict = {}
unique_dict = {}
common_name_dict = {}

# start looping through the tree
root = tree.getroot()
for node in root:  # Body
    for node2 in node:  # GetTaxonTreesBySearchCriteriaResponse
        for node3 in node2:  # GetTaxonTreesBySearchCriteriaResult
            for node4 in node3:  # WebTaxonTreeNode
                count += 1
                taxon_info = node4[2]
                taxon_id = taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}Id').text.encode('utf-8')
                taxon_name = taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}ScientificName').text.encode('utf-8')
                taxon_name = taxon_name.strip()
                taxon_author = taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}Author').text
                if taxon_author is None:
                    taxon_author = ""
                else:
                    taxon_author = taxon_author.encode('utf-8')
                taxon_author = taxon_author.strip()
                taxon_category = taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}CategoryId').text.encode('utf-8')
                taxon_is_valid = taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}IsValid').text.encode('utf-8')
                common_name = taxon_info.find('{http://schemas.datacontract.org/2004/07/ArtDatabanken.WebService.Data}CommonName').text
                if common_name is None:
                    common_name = ""
                else:
                    common_name = common_name.encode('utf-8')
                common_name = common_name.strip()

                if int(rank_dict[taxon_category]) >= int("70"):
                    taxon_name = taxon_name.replace("  ", " ")
                    temp_taxon_parts = taxon_name.split(" ", 2)
                    taxon_name = temp_taxon_parts[1]
                    if taxon_name == "":
                        err += 1
                        f.write("ERR: Taxon name (split) is empty (" + str(taxon_id) + ").\n")
                        exit()
                unique_dict[taxon_id] = "1"
                ids_dict[count] = taxon_id
                name_dict[count] = taxon_name
                author_dict[count] = taxon_author
                category_dict[count] = taxon_category
                parent_dict[count] = 0
                valid_dict[count] = taxon_is_valid
                common_name_dict[count] = common_name
                if node4[1] is not None:
                    get_children(node4[1], count, rank_dict[taxon_category])


# print out sorted dictionary
for p in sorted(ids_dict):
    m.write(str(p) + '\t' + str(parent_dict[p]) + '\t' + str(ids_dict[p]) + '\t' + str(name_dict[p]) + '\t' + str(author_dict[p]) + '\t' + str(category_dict[p]) + '\t' + str(rank_dict[category_dict[p]]) + '\t' + str(valid_dict[p]) + '\n')

f.close()
m.close()

# print out the number of correct taxa about to be added to db
total_count = count - err
print "\nTotal number of taxa: " + str(total_count)

# exit before API requests
# exit()

# create dicts to hold new db id-s and urls to refer back to parent_id-s
taxonomy_id_dict = {}
taxonomy_url_dict = {}

# create connection
conn = httplib.HTTPConnection('localhost:7000')
conn.request("GET", "/api/taxonomy/")
r1 = conn.getresponse()
print r1.status, r1.reason

# authorize
print "Authenticating..."
headers = {"Content-type": "application/x-www-form-urlencoded",
           "Accept": "text/plain"}
params = urllib.urlencode({'client_id': '4908fdadf35697117048',
                           'client_secret': '299191c8d310a3d818ac16f8f103711a3e968e14',
                           'grant_type': 'password',
                           'username': 'admin',
                           'password': 'pass',
                           'scope': 'write'})
conn.request("POST", "/oauth2/access_token/", params, headers)
response = conn.getresponse()
print response.status, response.reason
data = response.read()
json_data = json.loads(data)
access_token = json_data["access_token"]
token_type = json_data["token_type"]
token = token_type + ' ' + access_token

# POST new tree
if args.tree is None:
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "application/json", "Authorization": token}
    params = urllib.urlencode({'format': 'json', 'name': 'new tree'})
    conn.request("POST", "/api/taxonomy/tree/", params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    if response.status != 201:
        sys.exit
    data = response.read()
    json_data = json.loads(data)
    new_tree_id = json_data["id"]
    new_tree_url = json_data["url"]
    print "New tree added with id " + str(new_tree_id)
else:
    new_tree_id = args.tree
    new_tree_url = "http://localhost:7000/api/taxonomy/tree/" + str(args.tree) + "/"

# POST taxon node data
for p in sorted(ids_dict):
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "application/json", "Authorization": token}
    if int(parent_dict[p]) == int(0):
        tmp_taxon_rank = 'http://localhost:7000/api/taxonomy/taxon_rank/' + str(rank_dict[category_dict[p]]) + '/'
        params = urllib.urlencode({'format': 'json',
                                   'epithet': str(name_dict[p]),
                                   'tree': new_tree_url,
                                   'epithet_author': str(author_dict[p]),
                                   'taxon_rank': tmp_taxon_rank,
                                   'code': str(ids_dict[p])})
    else:
        tmp_taxon_rank = 'http://localhost:7000/api/taxonomy/taxon_rank/' + str(rank_dict[category_dict[p]]) + '/'
        params = urllib.urlencode({'format': 'json',
                                   'epithet': str(name_dict[p]),
                                   'tree': new_tree_url,
                                   'epithet_author': str(author_dict[p]),
                                   'taxon_rank': tmp_taxon_rank,
                                   'code': str(ids_dict[p]),
                                   'parent': str(taxonomy_url_dict[parent_dict[p]])})
    conn.request("POST", "/api/taxonomy/taxon/", params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    if response.status != 201:
        exit()
    data = response.read()
    json_data = json.loads(data)
    new_id = json_data["id"]
    new_url = json_data["url"]
    taxonomy_id_dict[p] = new_id
    taxonomy_url_dict[p] = new_url

    # check if there's vernacular name to be added
    if common_name_dict[p] != "":
        tmp_language = 'http://localhost:7000/api/taxonomy/language/swe/'
        params = urllib.urlencode({'format': 'json',
                                   'common_name': str(common_name_dict[p]),
                                   'iso_639': tmp_language,
                                   'taxon_node': new_url})
        conn.request("POST", "/api/taxonomy/vernacular_name/", params, headers)
        response = conn.getresponse()
        print response.status, response.reason
        if response.status != 201:
            exit()

# end here and print out runtime
print "Everything seemed to work smoothly, will stop here."
time_end_total = time.time()
print "Total time taken: %.2f seconds" % (time_end_total - time_start_total)
