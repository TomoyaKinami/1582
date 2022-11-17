global member_data
    id=request.form.get('id')
    pswd=request.form.get('pass')
    if id in member_data:
        if pswd==member_data[id]:
            session['login']=True
        else:
            session['login']=False
    else:
        member_data[id]=pswd
        session['login']=True
    session['id']=id
    if session['login']:
        return redirect('/')
    else:
        return render_template('login.html',\
            title='Login',\
                err=False,\
                    message='パスワードが違います。',\
                        id=id)



                        <script>
var list3=eval({{class_list3|tojson}};)

    Vue.component('mycomp',{
        template:'#mycomp-template',
        data:function(){
            return{data:list3};       
            }})
</script>

def create_class(x):
    card_title=x[1]
    card_teacher=x[2]
    card_place=x[3]
    return '<div class="card" style="width:18rem;"><div class="card-body"><h5 class="card-title">'+card_title+'</h5><p class="card-text">担当教員:'+card_teacher+'</p><p class="card-text">教室:'+card_place+'</p><a class="btn btn-primary">参加</a></div></div>'

    class_list2=[]
        for i in range(0,len(class_list)):
            class_list2.append(create_class(class_list[i]))
        class_list3=''.join(class_list2)


        <div class="card" style="width:18rem;"><div class="card-body"><h5 class="card-title">+card_title+</h5><p class="card-text">担当教員:'+card_teacher+'</p><p class="card-text">教室:'+card_place+'</p><a class="btn btn-primary">参加</a></div></div>

        {% endraw %}
<script>
var list3=eval({{class_list3|tojson}};)

    Vue.component('mycomp',{
        template:'#mycomp-template',
        data:function(){
            return{data:list3};       
            }})
</script>
{% endblock %}

<div id="app" class="m-3">
    <mycomp />
</div>

{% raw %}
<script type='text/x-template' id='mycomp-template'>