#!/usr/bin/env python3

import requests
import pandas as pd
from collections import namedtuple
import os

class botDefaults:
    defaultServer = ""
    defaultRegion = ""

    def setRegion(self,region):
        self.defaultRegion = region

    def setServer(self,server):
        self.defaultServer = server

class FflogsRequest:

    def __init__(self):
        self.domain = 'www.fflogs.com/v1'
        self.fflogs_url = 'https://{}'.format(self.domain)
        self.url_endpoint = {
            'zones' : '/zones',
            'classes' : '/classes',
            'rankings' : '/rankings',
            'parses' : '/parses',
            'reports': '/reports',
            'report' : '/report'
        }
        self.api_key = os.getenv('FFLOGS_API_KEY')
        self.session = requests.Session()
        self.all_encounters = self.get_all_encounters()
        self.all_specs = self.get_all_specs()
        # self.latest_encounters = self.get_latest_encounters()

    def make_request(self, url=None):
        final_url = url.replace(" ", "%20")
        print (final_url)
        return self.session.get(final_url)


    def get_zone_url(self):
        request_url = "{}{}?api_key={}".format(self.fflogs_url, self.url_endpoint["zones"], self.api_key)
        return request_url

    def get_class_url(self):
        request_url = "{}{}?api_key={}".format(self.fflogs_url, self.url_endpoint["classes"], self.api_key)
        return request_url

    def get_ranking_url(self, **kwargs):
        parms = '/'.join([kwargs[key] for key in kwargs])
        request_url = "{}{}/{}?api_key={}".format(self.fflogs_url, self.url_endpoint["rankings"], parms, self.api_key)
        return request_url

    def get_parses_url(self, **kwargs):
        parms = '/'.join([kwargs[key] for key in kwargs])
        request_url = "{}{}/{}?api_key={}".format(self.fflogs_url, self.url_endpoint["parses"], parms, self.api_key)
        return request_url

    def ordinal_suffix_of(self,num):
        i = num % 10
        j = num % 100

        if (i == 1 and j != 11):
            return str(num) + "st"
        elif (i == 2 and j != 12):
            return str(num) + "nd"
        elif (i == 3 and j != 13):
            return str(num) + "rd"
        else:
            return str(num) + "th"


    def get_all_encounters(self):
        response = self.make_request(self.get_zone_url())

        if response.ok:
            # response returns list of zones
            zones = response.json()
            every_encounter = []

            # each zone is a dictionary
            for zone in zones:
                # For every encounter in a zone
                # zone['encounters'] is a list of encounter
                # encounter is a dictionary
                for encounter in zone['encounters']:
                    encounter['parent_id'] = zone['id']
                    every_encounter.append(encounter)

            return every_encounter

    # def get_latest_encounters(self):
    #     response = self.make_request(self.get_zone_url())
    #
    #     if response.ok:
    #         # response returns list of zones
    #         zones = response.json()
    #
    #         # get the latest zone's encounters
    #         max_zone = max(zones, key=lambda zone: zone['id'])
    #
    #         # gets every latest encounter
    #         latest_encounter = []
    #         for encounter in max_zone['encounters']:
    #             encounter['parent_id'] = max_zone['id']
    #             latest_encounter.append(encounter)
    #
    #         return latest_encounter

    def get_all_specs(self):
        response = self.make_request(self.get_class_url())

        if response.ok:
            # Response will be a list with a single dictionary element
            r = response.json()
            return r[0]['specs']
        return ''


    def get_encounter_id(self,name):
        for encounter in self.all_encounters:
            if name == encounter['name']:
                return encounter['id']
        return ''


    def get_encounter_name(self,id):
        for encounter in self.all_encounters:
            if id == encounter['id']:
                return encounter['name']
        return


    def get_spec_name(self,spec_id):
        for spec in self.all_specs:
            if spec['id'] == spec_id:
                return spec['name']
        return ''


    def rank_of(self, name, server, region):
        url = self.get_ranking_url(character="character", name=name, server=server, region=region)
        response = self.make_request(url)

        columns = ['job', 'name', 'encounter', 'rank', 'rank_out_of', 'total_dps']
        rank_data = []
        if response.ok:
            encounters = response.json()
            for encounter in encounters:
                job = self.get_spec_name(encounter['spec'])
                e = self.get_encounter_name(encounter['encounter'])
                rank = encounter['rank']
                rank_out_of = encounter['outOf']
                total_dps = encounter['total']
                rank_data.append((job, name, e, rank, rank_out_of, total_dps))
        return pd.DataFrame(data=rank_data, columns=columns)

    def best_percentile_of(self, name, server, region):
        url = self.get_parses_url(character="character", name=name, server=server, region=region)
        response = self.make_request(url)

        columns = ['job', 'name', 'best_dps', 'best_hist_pct']
        best_of_data = []
        if response.ok:
            json_response = response.json()
            for encounter in json_response:
                best_of_specs = encounter['specs']
                for i,value in enumerate(best_of_specs):
                    job = best_of_specs[i].get('spec')
                    best_hist_pct = best_of_specs[i].get('best_historical_percent')
                    best_dps = best_of_specs[i].get('best_persecondamount')
                    best_of_data.append((job, name, best_dps, best_hist_pct))
        return pd.DataFrame(data=best_of_data, columns=columns)


    def current_percentile_of(self, name, server, region):
        url = self.get_parses_url(character="character", name=name, server=server, region=region)
        response = self.make_request(url)

        columns = ['job', 'name', 'curr_dps', 'curr_pct']
        curr_data = []
        if response.ok:
            json_response = response.json()
            for encounter in json_response:
                current_specs = encounter.get('specs')
                for s in current_specs:
                    job = s['spec']
                    curr_pct = int(s['data'][0]['percent'])
                    curr_dps = s['data'][0]['persecondamount']
                    curr_data.append((job, name, curr_dps, curr_pct))

        return pd.DataFrame(data=curr_data, columns=columns)


    def get_max_encounter(self, name, server, region):
        url = '{}/parses/character/%s/%s/%s?api_key=%s'.format(self.fflogs_url,name,server,region,self.api_key)
        response = self.make_request(url)

        if response.ok:
            encounters = response.json()

            """
                [] Valid character name but no uploaded logs
                {'hidden':true} Hidden logs
            """
            if not encounters or isinstance(encounters, dict):
                return

            """
                [{},{}...] List of encounters where each encounter is a dictionary
            """
            for encounter in encounters:
                encounter['encounter_id'] = self.get_encounter_id(encounter['name'])

            return max(encounters, key=lambda encounter: encounter['encounter_id'])

    def get_max_encounter_per_patch(self,name,server,region,patch):
        url = '{}/parses/character/{}/{}/{}?api_key={}'.format(self.fflogs_url,name,server,region,self.api_key)
        response = self.make_request(url)
        if response.ok:
            encounters = response.json()

            #[] Valid character name but no uploaded logs
            #{'hidden':true} Hidden logs
            if not encounters or isinstance(encounters, dict):
                return ''

            #[{},{}...] List of encounters where each encounter is a dictionary
            patch = float(patch)
            patch_encounters = []

            for encounter in encounters:
                specs = encounter['specs']
                for spec in specs:
                    data = spec['data']
                    for d in data:
                        if d['ilvl'] == patch:
                            pe = { 'name' : encounter['name'], 'id': self.get_encounter_id(encounter['name']) }
                            patch_encounters.append(pe)

            if patch_encounters:
                return (max(patch_encounters, key=lambda x: x['id'])).get('name')


if __name__ == "__main__":
    #scraper= lodestone_scraper.LodestoneScraper()
    f = FflogsRequest()
    x = (f.rank_of("Roshan Crass", "Gilgamesh", "NA"))
