function sendPoodleForm(){
    jq("#poodleForm [name=form.button.Save]").live("click", function(e){
            e.stopPropagation();
            e.preventDefault();
            var infos = jq("#"+this.id).closest('form#poodleForm').serializeArray();
            var base_href = jq('base')[0].href;
            jq.post(base_href+'jq_submit_data', infos, function(callback){

                    jq.post(base_href+'izug_poodle_table', infos, function(data){
                        jq('#poodltablewrapper_'+infos[infos.length -1].value).html(data);
                    });
                    
                    jq('#kssPortalMessage').show();
                    jq('#kssPortalMessage dd').html(callback);

                });
        });

}

function abordPoodleForm(){
    jq("[name=form.button.Cancel_poodle]").live("click", function(e){
                e.stopPropagation();
                e.preventDefault();
                var base_href = jq('base')[0].href;
                var infos = jq(this).closest('form#poodleForm').serializeArray();
                infos.push({"name":"appendix", "value":$(this).attr("id")});
                jq.post(base_href+'izug_poodle_table', infos, function(data){
                    jq('#poodltablewrapper_'+infos[infos.length -1].value).html(data);
                });


        });

}


function chooseEvent(){
    jq('.buttonContainer [name=subform.submit.button]').live('click',function(e){
            var params = jq(this).closest('form').serializeArray();
            var base_href = jq('base')[0].href;
            jq.post(base_href+'convert_to_meeting',params,function(data){
                    if (data){
                        top.location = base_href;    
                    } 
                });
            e.stopPropagation();
            e.preventDefault();
        })
}


jq(chooseEvent);
jq(abordPoodleForm);
jq(sendPoodleForm);
