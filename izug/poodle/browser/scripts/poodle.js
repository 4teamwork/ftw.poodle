function sendPoodleForm(){
    jq("#poodleForm [name=form.button.Save]").live("click", function(e){
            infos = jq("#"+this.id).closest('form#poodleForm').serializeArray();
            base_href = jq('base')[0].href;
            jq.post(base_href+'/jq_submit_data', infos, function(callback){

                    jq.post(base_href+'/izug_poodle_table', infos, function(data){
                        jq('#poodltablewrapper_'+infos[infos.length -1].value).html(data)
                    });

                });
            e.stopPropagation();
            e.preventDefault();
        });

}

function abordPoodleForm(){
    jq("[name=form.button.Cancel]").live("click", function(e){
                base_href = jq('base')[0].href;

                jq.post(base_href+'/izug_poodle_table', infos, function(data){
                    jq('#poodltablewrapper_'+infos[infos.length -1].value).html(data)
                });

            e.stopPropagation();
            e.preventDefault();
        });

}


jq(abordPoodleForm);
jq(sendPoodleForm);
