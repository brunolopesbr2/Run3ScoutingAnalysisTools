import gzip, json

with gzip.open("jetScouting_jerc.json.gz") as f:
    scouting = json.load(f)
with gzip.open("jet_jerc.json.gz") as f:
    offline_Summer24 = json.load(f)

wanted = {
    "Summer24Prompt24_JRV2_MC_PtResolution_AK4PFPuppi",
    "Summer24Prompt24_JRV2_MC_ScaleFactor_AK4PFPuppi",
    "Summer24Prompt24_JRV2_MC_SFUncertainty_AK4PFPuppi"
}
found = {c["name"] for c in offline_Summer24["corrections"]} & wanted
print("found:", found, "missing:", wanted - found)   # sanity check before merging

scouting["corrections"] += [c for c in offline_Summer24["corrections"] if c["name"] in wanted]

with gzip.open("jetScouting_jerc_withPuppiJER.json.gz", "wt") as f:
    json.dump(scouting, f)