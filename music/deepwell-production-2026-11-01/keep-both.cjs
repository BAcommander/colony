const fs=require('fs'),path=require('path');const H=__dirname,R=path.resolve(H,'../..');
const feedback={date:'2026-11-01',verbatim:'Keep both as candidates',decision:'Retain Waterworks Gallery and Sheltered Replenishment as candidates',single_selected_track:null,approval_for_final_mix:false,approval_to_blend_or_alternate_not_inferred:true};
fs.writeFileSync(path.join(H,'user-feedback.json'),JSON.stringify(feedback,null,2)+'\n');
for(const relative of ['music/deepwell-production-2026-11-01/sample-intake.json','final/12-deepwell-station/music/generation-record.json']){
 const p=path.join(R,relative),d=JSON.parse(fs.readFileSync(p,'utf8'));d.user_feedback=feedback;d.candidate_decision='Keep both as candidates';fs.writeFileSync(p,JSON.stringify(d,null,2)+'\n');
}
console.log('User decision recorded: retain both candidates; no final selection inferred');
