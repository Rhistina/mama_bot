#!/usr/bin/env python3

import requests

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
        self.session = requests.Session()
        self.api_key = ''
        self.all_encounters = self.get_all_encounters()
        self.all_specs = self.get_all_specs()
        self.latest_encounters = self.get_latest_encounters()


    def make_request(self, url=None):
        final_url = url.replace(" ", "%20")
        print (final_url)
        return self.session.get(final_url)


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
        url = "{}/zones?api_key={}".format(self.fflogs_url,self.api_key)
        response = self.make_request(url)

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

    def get_latest_encounters(self):
        url = "{}/zones?api_key={}".format(self.fflogs_url,self.api_key)
        response = self.make_request(url)

        if response.ok:
            # response returns list of zones
            zones = response.json()

            # get the latest zone's encounters
            max_zone = max(zones, key=lambda zone: zone['id'])

            # gets every latest encounter
            latest_encounter = []
            for encounter in max_zone['encounters']:
                encounter['parent_id'] = max_zone['id']
                latest_encounter.append(encounter)

            return latest_encounter

    def get_all_specs(self):
        url = '{}/classes?api_key={}'.format(self.fflogs_url, self.api_key)
        print (url)
        response = self.make_request(url)

        if response.ok:
            # Response will be a list with a single dictionary element
            r = response.json()
            return r[0]['specs']

        return

    def get_encounter_id(self,name):
        for encounter in self.all_encounters:
            if name == encounter['name']:
                return encounter['id']
        return


    def get_encounter_name(self,id):
        for encounter in self.all_encounters:
            if id == encounter['id']:
                return encounter['name']
        return

    def get_spec_name(self,spec_id):
        for spec in self.all_specs:
            if spec['id'] == spec_id:
                return spec['name']
        return

    def rank_of(self,name,server,region):
        url = '{}/rankings/character/{}/{}/{}?api_key={}'.format(self.fflogs_url,name,server,region,self.api_key)
        response = self.make_request(url)

        if response.ok:
            encounters = response.json()
            filler = '`______________`'
            string = ""
            numEncounters = 0
            for encounter in encounters:
                numEncounters += 1
                if (numEncounters <=15):
                    encounterName = self.get_encounter_name(encounter['encounter'])
                    rank = encounter['rank']
                    outOf = encounter['outOf']
                    totalDps = encounter['total']
                    specName = self.get_spec_name(encounter['spec'])
                    string += ("As a **%s**, %s has cleared %s and ranked %s out of %s doing a total of **%s DPS**." % (specName,name,encounterName,rank,outOf,totalDps)) + '\n'
                else:
                    break

            messageToReply = ('Current Rankings for %s \n' % (name))
            if (numEncounters > 15):
                messageToReply = ('Current Rankings for %s (Number of ranks displayed capped at 15)\n' % (name))

            messageToReply += string

            #print (messageToReply)
            return messageToReply

        return response.reason

    def best_percentile_of(self,name,server,region):
        url = '{}/parses/character/{}/{}/{}?api_key={}'.format(self.fflogs_url,name,server,region,self.api_key)
        response = self.make_request(url)

        if response.ok:
            messageToReply = ""
            filler = '`________________________________`\n'

            # json_response is a list of dictionaries
            json_response = response.json()

            messageToReply += ('Best Historical Percentiles for %s\n' % (name))
            string = ""
            #each dictionary is a encounter
            for encounter in json_response:
                string += filler
                string += encounter.get('name') + '\n'

                #specs is a list of dictionaries
                best_of_specs = encounter['specs']

                for x in range(len(best_of_specs)):
                    specName = best_of_specs[x].get('spec')
                    bestHistoricalPct = best_of_specs[x].get('best_historical_percent')
                    bestDpsAmt = best_of_specs[x].get('best_persecondamount')
                    string += ("As a **%s**, %s did **%s DPS** with a best historical **percentile of %s**." % (specName, name,bestDpsAmt,bestHistoricalPct)) + '\n'

            messageToReply += string
            return messageToReply


    def current_percentile_of(self,name,server,region):
        url = '{}/parses/character/{}/{}/{}?api_key={}'.format(self.fflogs_url, name, server, region, self.api_key)
        response = self.make_request(url)

        if response.ok:
            messageToReply = ""
            filler = '`________________________________`\n'

            # json_response is a list of dictionaries
            json_response = response.json()

            messageToReply += ('Current Percentiles for %s\n' % (name))
            strng = ""

            #each dictionary is a encounter
            for encounter in json_response:
                strng += filler
                strng += encounter.get('name') + '\n'

                #specs is a list of dictionaries
                current_specs = encounter.get('specs')

                for s in current_specs:
                    spec_name = s['spec']
                    current_spec_pct = int(s['data'][0]['percent'])
                    current_spec_parse = s['data'][0]['persecondamount']
                    strng += "As a **%s**, %s did **%s DPS** with a current **percentile of %s**." % (spec_name, name, current_spec_parse, current_spec_pct) + '\n'

            messageToReply += strng
            return messageToReply
        return


    def get_max_encounter(self,name,server,region):
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
            """
                [] Valid character name but no uploaded logs
                {'hidden':true} Hidden logs
            """
            if not encounters or isinstance(encounters, dict):
                return

            """
                [{},{}...] List of encounters where each encounter is a dictionary
            """
            patch = float(patch)
            listOfPatchEncounters = []

            max_zone = max(self.latest_encounters, key=lambda encounter: encounter['id'])
            print (max_zone)

            for encounter in encounters:
                specs = encounter['specs']
                for spec in specs:
                    data = spec['data']
                    for d in data:
                        if d['ilvl'] == patch:
                            pencounter = { 'name' : encounter['name'], 'id': self.get_encounter_id(encounter['name']) }
                            listOfPatchEncounters.append(pencounter)

            if listOfPatchEncounters:
                return max(listOfPatchEncounters, key=lambda pencounter: pencounter['id'])
        else:
            return ("Error:{}, Message:{}".format(response.status_code,response.json()['error']))

if __name__ == "__main__":
    #scraper= lodestone_scraper.LodestoneScraper()
    f = FflogsRequest()

    #print(f.get_spec_name(4))
    #print(f.current_percentile_of("Roshan Crass", "Gilgamesh", "NA"))
    #print(f.get_max_encounter_per_patch("Roshan Crass", "Gilgamesh", "NA", 3.4))
    #print(f.best_percentile_of("Roshan Crass", "Gilgamesh", "NA"))
    #print(f.rank_of("Roshan Crass", "Gilgamesh", "NA"))
    #print (f.get_latest_encounters())

