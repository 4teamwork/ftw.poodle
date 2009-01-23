function sendPoodleForm(){
    jq("#poodleForm [@name=form.button.Save]").bind("click", function(e){
            infos = jq(".poodle_view form").serializeArray();
            base_href = jq('base')[0].href;
            jq.post(base_href+'/jq_submit_data', infos, function(callback){

                    jq.post(base_href+'/izug_poodle_table',function(data){
                        jq('#poodltablewrapper').html(data)
                    });

                });
            e.stopPropagation();
            e.preventDefault();
        });

}

function abordPoodleForm(){
    jq("[@name=form.button.Cancel]").bind("click", function(e){
                base_href = jq('base')[0].href;

                jq.post(base_href+'/izug_poodle_table',function(data){
                    jq('#poodltablewrapper').html(data)
                });

            e.stopPropagation();
            e.preventDefault();
        });

}


jq(abordPoodleForm);
jq(sendPoodleForm);
