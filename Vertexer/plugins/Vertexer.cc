// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/Vertexer
// Class:      Vertexer
//
/**\class Vertexer Vertexer.cc Run3ScoutingAnalysisTools/Vertexer/plugins/Vertexer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Bruno Lopes
//         Created:  Wed, 04 Sep 2024 12:37:22 GMT
//
//

// system include files
#include <memory>

#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "MagneticField/Engine/interface/MagneticField.h"

// user include files
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/Utilities/interface/ESGetToken.h"
#include "DataFormats/Common/interface/ValueMap.h"

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

//Scouting data formats
#include "DataFormats/Scouting/interface/Run3ScoutingElectron.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPhoton.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPFJet.h"
#include "DataFormats/Scouting/interface/Run3ScoutingVertex.h"
#include "DataFormats/Scouting/interface/Run3ScoutingTrack.h"
#include "DataFormats/Scouting/interface/Run3ScoutingMuon.h"
#include "DataFormats/Scouting/interface/Run3ScoutingParticle.h"

//Vertex tools
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"
#include "RecoVertex/VertexTools/interface/VertexDistance3D.h"
#include "RecoVertex/VertexTools/interface/VertexDistanceXY.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"


using namespace edm;

//
// class declaration
//

class Vertexer : public edm::stream::EDProducer<> {
public:
  ~Vertexer() override;

  explicit Vertexer(edm::ParameterSet const& params);
  //static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  typedef std::set<reco::TrackRef> track_set;
  typedef std::vector<reco::TrackRef> track_vec;

  void beginStream(edm::StreamID) override;
  void produce(edm::Event&, const edm::EventSetup&) override;
  void endStream() override;


  const int n_tracks_per_seed_vertex;
  const double max_seed_vertex_chi2;
  const bool use_2d_vertex_dist;
  const bool use_2d_track_dist;
  const bool remove_one_track_at_a_time;
  const double merge_shared_dist;
  const double merge_shared_sig;
  const double max_track_vertex_dist;
  const double max_track_vertex_sig;
  const double min_track_vertex_sig_to_remove;
  
  const edm::EDGetTokenT<std::vector<reco::Track>> seed_tracks_token_;
  const edm::ESGetToken<TransientTrackBuilder, TransientTrackRecord> token_builder;

  edm::EDPutTokenT<reco::VertexCollection> putToken_;

  //void beginRun(edm::Run const&, edm::EventSetup const&) override;
  //void endRun(edm::Run const&, edm::EventSetup const&) override;
  //void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
  //void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

  // ----------member data ---------------------------

  //Will get the beamspot from the GT later. For now, set it =0 to test
  float bsx = 0;
  float bsy = 0;
  float bsz = 0;

  VertexDistanceXY vertex_dist_2d;
  VertexDistance3D vertex_dist_3d;

  bool is_track_subset(const track_set & a, const track_set & b) const {
    bool is_subset = true;
    const track_set& smaller = a.size() <= b.size() ? a : b;
    const track_set& bigger = a.size() <= b.size() ? b : a;
    
    for (auto t : smaller)
      if (bigger.count(t) < 1) {
	is_subset = false;
	break;
      }
    
    return is_subset;
  }
  
  
  Measurement1D vertex_dist(const reco::Vertex & v0, const reco::Vertex & v1) {
    if (use_2d_vertex_dist)
      return vertex_dist_2d.distance(v0, v1);
    else
      return vertex_dist_3d.distance(v0, v1);
  }
  
  track_set vertex_track_set(const reco::Vertex & v, const double min_weight = 0.5) {
    track_set result;

    //reco::Track track_test;
    
    for (auto it = v.tracks_begin(), ite = v.tracks_end(); it != ite; ++it) {
      const double w = v.trackWeight(*it);
      const bool use = w >= min_weight;
      assert(use);

      if (use) {
	const auto theTrackRef = it->castTo<reco::TrackRef>();
	result.insert(theTrackRef);
      }
    }
    
    return result;
    }

  /* //Returns an empty track_set to test the function above
  track_set vertex_track_set(const reco::Vertex & v, const double min_weight = 0.5) {
    track_set result;
    return result; }
  */
  
  
  std::pair<bool, Measurement1D> track_dist(const reco::TransientTrack & t, const reco::Vertex & v) const {
    if (use_2d_track_dist)
      return IPTools::absoluteTransverseImpactParameter(t, v);
    else
      return IPTools::absoluteImpactParameter3D(t, v);
  }
  
  
};


//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//

Vertexer::Vertexer(edm::ParameterSet const& params)
  :
  n_tracks_per_seed_vertex(params.getParameter<int>("n_tracks_per_seed_vertex")),
  max_seed_vertex_chi2(params.getParameter<double>("max_seed_vertex_chi2")),
  use_2d_vertex_dist(params.getParameter<bool>("use_2d_vertex_dist")),
  use_2d_track_dist(params.getParameter<bool>("use_2d_track_dist")),
  remove_one_track_at_a_time(params.getParameter<bool>("remove_one_track_at_a_time")),
  merge_shared_dist(params.getParameter<double>("merge_shared_dist")),
  merge_shared_sig(params.getParameter<double>("merge_shared_sig")),
  max_track_vertex_dist(params.getParameter<double>("max_track_vertex_dist")),
  max_track_vertex_sig(params.getParameter<double>("max_track_vertex_sig")),
  min_track_vertex_sig_to_remove(params.getParameter<double>("min_track_vertex_sig_to_remove")),
  
  seed_tracks_token_(consumes(params.getParameter<edm::InputTag>("seed_tracks_src"))),
  token_builder(esConsumes(edm::ESInputTag("", "TransientTrackBuilder"))),
  putToken_{produces()} {}

Vertexer::~Vertexer() {}

//
// member functions
//

KalmanVertexFitter kv_reco;
std::vector<TransientVertex> kv_reco_dropin(std::vector<reco::TransientTrack> & ttks) {
  if (ttks.size() < 2)
    return std::vector<TransientVertex>();
  std::vector<TransientVertex> v(1, kv_reco.vertex(ttks));
  if (v[0].normalisedChiSquared() > 5)
    return std::vector<TransientVertex>();
  return v;
}


// ------------ method called to produce the data  ------------
void Vertexer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {

  //Get the Transient Track Builder
  auto const &tt_builder = iSetup.getData(token_builder);

  //Get the reco tracks from the events
  edm::Handle<std::vector<reco::Track>> seed_track_handle;
  iEvent.getByToken(seed_tracks_token_, seed_track_handle);


  //  const edm::Ref<reco::Track> leadingTrackRef(seed_track_refs, 0);

  //Build transient tracks from reco tracks
  std::vector<reco::TransientTrack> seed_tracks = tt_builder.build(seed_track_handle);


  std::vector<reco::TrackRef> seed_track_refs;

  for (size_t i_tk = 0; i_tk < seed_track_handle->size(); i_tk++){
    const edm::Ref<reco::TrackCollection> tk_ref(seed_track_handle, i_tk);
    seed_track_refs.push_back(tk_ref);
  }
  
  //Former map from tracks to the number of seed tracks
  std::map<reco::TrackRef, size_t> seed_track_ref_map;
  for (const reco::TrackRef& tk : seed_track_refs) {
    seed_track_ref_map[tk] = seed_tracks.size() - 1;
  }
  
  //const size_t seed_track_ref_map[tk] = seed_tracks.size() - 1;
  

  //////////////////////////////////////////////////////////////////////
  // Form seed vertices from all pairs of tracks whose vertex fit
  // passes cuts.
  //////////////////////////////////////////////////////////////////////
  
  reco::VertexCollection vertices;
  
  const size_t ntk = seed_tracks.size();
  //printf("n_seed_tracks: %5lu\n", ntk);

  std::vector<size_t> itks(n_tracks_per_seed_vertex, 0);

  auto try_seed_vertex = [&]() {
    std::vector<reco::TransientTrack> ttks(n_tracks_per_seed_vertex);
    for (int i = 0; i < n_tracks_per_seed_vertex; ++i)
      ttks[i] = seed_tracks[itks[i]];

    TransientVertex seed_vertex = kv_reco.vertex(ttks);
    if (seed_vertex.isValid() && seed_vertex.normalisedChiSquared() < max_seed_vertex_chi2) { 
      vertices.push_back(reco::Vertex(seed_vertex));
    }
  };
			 
  // ha
  for (size_t itk = 0; itk < ntk; ++itk) {
    itks[0] = itk;
    for (size_t jtk = itk + 1; jtk < ntk; ++jtk) {
      itks[1] = jtk;
      if (n_tracks_per_seed_vertex == 2) { try_seed_vertex(); continue; }
      for (size_t ktk = jtk + 1; ktk < ntk; ++ktk) {
        itks[2] = ktk;
        if (n_tracks_per_seed_vertex == 3) { try_seed_vertex(); continue; }
        for (size_t ltk = ktk + 1; ltk < ntk; ++ltk) {
          itks[3] = ltk;
          if (n_tracks_per_seed_vertex == 4) { try_seed_vertex(); continue; }
          for (size_t mtk = ltk + 1; mtk < ntk; ++mtk) {
            itks[4] = mtk;
            try_seed_vertex();
          }
        }
      }
    }
  }

  //////////////////////////////////////////////////////////////////////
  // Take care of track sharing. If a track is in two vertices, and
  // the vertices are "close", refit the tracks from the two together
  // as one vertex. If the vertices are not close, keep the track in
  // the vertex to which it is "closer".
  //////////////////////////////////////////////////////////////////////

  track_set discarded_tracks;
  int n_resets = 0;
  int n_onetracks = 0;
  std::vector<reco::Vertex>::iterator v[2];

  for (v[0] = vertices.begin(); v[0] != vertices.end(); ++v[0]) {
    track_set tracks[2];
    tracks[0] = vertex_track_set(*v[0]);

    if (tracks[0].size() < 2) {
      v[0] = vertices.erase(v[0]) - 1;
      ++n_onetracks;
      continue;
    }

    bool duplicate = false;
    bool merge = false;
    bool refit = false;
    track_set tracks_to_remove_in_refit[2];

    for (v[1] = v[0] + 1; v[1] != vertices.end(); ++v[1]) {
      tracks[1] = vertex_track_set(*v[1]);

      if (tracks[1].size() < 2) {
	v[1] = vertices.erase(v[1]) - 1;
        ++n_onetracks;
        continue;
      }


      if (is_track_subset(tracks[0], tracks[1])) {
        duplicate = true;
        break;
      }

      std::vector<reco::TrackRef> shared_tracks;
      for (auto tk : tracks[0])
        if (tracks[1].count(tk) > 0)
          shared_tracks.push_back(tk);


      Measurement1D v_dist = vertex_dist(*v[0], *v[1]);
      
      if (v_dist.value() < merge_shared_dist || v_dist.significance() < merge_shared_sig) {
	merge = true;
      }
      else
	refit = true;

            
      for (auto tk : shared_tracks) {
	const reco::TransientTrack& ttk = seed_tracks[seed_track_ref_map[tk]];
	std::pair<bool, Measurement1D> t_dist_0 = track_dist(ttk, *v[0]);
	std::pair<bool, Measurement1D> t_dist_1 = track_dist(ttk, *v[1]);
      

	t_dist_0.first = t_dist_0.first && (t_dist_0.second.value() < max_track_vertex_dist || t_dist_0.second.significance() < max_track_vertex_sig);
	t_dist_1.first = t_dist_1.first && (t_dist_1.second.value() < max_track_vertex_dist || t_dist_1.second.significance() < max_track_vertex_sig);
	bool remove_from_0 = !t_dist_0.first;
	bool remove_from_1 = !t_dist_1.first;
	if (t_dist_0.second.significance() < min_track_vertex_sig_to_remove && t_dist_1.second.significance() < min_track_vertex_sig_to_remove) {
	  if (tracks[0].size() > tracks[1].size())
	    remove_from_1 = true;
	  else
	    remove_from_0 = true;
	}
	else if (t_dist_0.second.significance() < t_dist_1.second.significance())
	  remove_from_1 = true;
	else
	  remove_from_0 = true;
	
	if (remove_from_0) tracks_to_remove_in_refit[0].insert(tk);
	if (remove_from_1) tracks_to_remove_in_refit[1].insert(tk);
	
	if (remove_one_track_at_a_time) break;
      }
      
      break;
    }

    if (duplicate) {
      vertices.erase(v[1]);
    }
    
    else if (merge) {
      track_set tracks_to_fit;
      for (int i = 0; i < 2; ++i)
        for (auto tk : tracks[i])
          tracks_to_fit.insert(tk);

      std::vector<reco::TransientTrack> ttks;
      for (auto tk : tracks_to_fit)
	ttks.push_back(seed_tracks[seed_track_ref_map[tk]]);
      
      reco::VertexCollection new_vertices;
      
      for (const TransientVertex& tv : kv_reco_dropin(ttks))
	new_vertices.push_back(reco::Vertex(tv));
    
      // If we got two new vertices, maybe it took A B and A C D and made a better one from B C D, and left a broken one A B! C! D!.
      // If we get one that is truly the merger of the track lists, great. If it is just something like A B , A C . A B C!, or we get nothing, then default to arbitration.
      if (new_vertices.size() > 1) {
        assert(new_vertices.size() == 2);
        *v[1] = reco::Vertex(new_vertices[1]);
        *v[0] = reco::Vertex(new_vertices[0]);
      }
      else if (new_vertices.size() == 1 && vertex_track_set(new_vertices[0], 0) == tracks_to_fit) {
        vertices.erase(v[1]);
        *v[0] = reco::Vertex(new_vertices[0]); // ok to use v[0] after the erase(v[1]) because v[0] is by construction before v[1]
      }
      else refit = true;

    }
      if (refit) {
	bool erase[2] = { false };
	reco::Vertex vsave[2] = { *v[0], *v[1] };

	for (int i = 0; i < 2; ++i) {
	  if (tracks_to_remove_in_refit[i].empty())
	    continue;

        std::vector<reco::TransientTrack> ttks;
        for (auto tk : tracks[i])
          if (tracks_to_remove_in_refit[i].count(tk) == 0)
            ttks.push_back(seed_tracks[seed_track_ref_map[tk]]);

        reco::VertexCollection new_vertices;
        for (const TransientVertex& tv : kv_reco_dropin(ttks)){
          new_vertices.push_back(reco::Vertex(tv));
        }
        if (new_vertices.size() == 1)
          * v[i] = new_vertices[0];
        else
          erase[i] = true;
	}

      if (erase[1]) vertices.erase(v[1]);
      if (erase[0]) vertices.erase(v[0]);

      }

    // If we changed the vertices at all, start loop over completely.
    if (duplicate || merge || refit) {
      v[0] = vertices.begin() - 1;  // -1 because about to ++sv
      ++n_resets;

      //if (n_resets == 3000)
      //  throw "I'm dumb";
    }
  }

//checkpoint

  
  //////////////////////////////////////////////////////////////////////////////////////////////
  // Merge vertices that are still "close" in 2D, aka "loose" merging (typically off by default)
  //////////////////////////////////////////////////////////////////////////////////////////////
  
  //////////////////////////////////////////////////////////////////////
  // Drop tracks that "move" the vertex too much by refitting without each track.
  //////////////////////////////////////////////////////////////////////

  /////////////////////////////////////////////////////////////////////////////////////////////////////
  // Merge every pair of output vertices that satisfy the following criteria to resolve split-vertices:
  //   - >=2trk/vtx
  //   - dBV > 100 um
  //   - |dPhi(vtx0,vtx1)| < 0.5 
  //   - svdist2d < 300 um
  // Note that the merged vertex must pass chi2/dof < 5
  ////////////////////////////////////////////////////////////////////////////////////////////////////


  //////////////////////////////////////////////////////////////////////
  // Put the output.
  //////////////////////////////////////////////////////////////////////
  
  //Save the vertices
  iEvent.emplace(putToken_, std::move(vertices));
}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void Vertexer::beginStream(edm::StreamID) {
  // please remove this method if not needed
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void Vertexer::endStream() {
  // please remove this method if not needed
}

// ------------ method called when starting to processes a run  ------------
/*
void
Vertexer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a run  ------------
/*
void
Vertexer::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when starting to processes a luminosity block  ------------
/*
void
Vertexer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
Vertexer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

/* ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void Vertexer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
*/

//define this as a plug-in
DEFINE_FWK_MODULE(Vertexer);
