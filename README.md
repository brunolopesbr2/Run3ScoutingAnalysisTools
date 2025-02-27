This branch is under development. It is intended to have a framework to deal with data.

The data processing will be the following:

- Start from HLTSCOUT data format
- Get reco::Vertex from the unpacker
- Run the Vertexer
- Repack the new vertices in the scouting format
- Create ScoutingNano + new vertices
- Move to a framework such as Coffea
