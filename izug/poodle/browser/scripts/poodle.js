function sendPoodleForm(){
    jq("[@name=form.button.Save]").bind("click", function(e){
            infos = jq(".poodle_view form").serializeArray();
            
            jq.post('eine-umfrage/jq_submit_data', infos, function(callback){

                    jq.post('eine-umfrage/izug_poodle_table',function(data){
                        jq('#poodltablewrapper').html(data)
                    });

                });
            e.stopPropagation();
            e.preventDefault();
        });

}

jq(sendPoodleForm);