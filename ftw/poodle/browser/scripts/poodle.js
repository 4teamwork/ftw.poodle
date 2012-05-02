function sendPoodleForm(){
    jq("#poodleForm [name=form.button.Save]").live("click", function(e){
            e.stopPropagation();
            e.preventDefault();
            var infos = jq("#"+this.id).closest('form#poodleForm').serializeArray();
            var base_href = jq('base')[0].href;
            jq.post(base_href+'/jq_submit_data', infos, function(callback){
                jq.post(base_href+'/ftw_poodle_table', infos, function(data){
                    jq('#poodltablewrapper_'+infos[infos.length -1].value).html(data);
                });
            });
        });

}
jq(sendPoodleForm);
