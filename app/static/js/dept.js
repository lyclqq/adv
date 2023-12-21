function dept_add() {
    const info61 = document.getElementById('info61')
    info61.innerText = ''
    const dept_form = document.getElementById('dept_form')

    const v1 = document.getElementById('groupname').validity.valid
    const v2 = document.getElementById('type').validity.valid
    const v3 = document.getElementById('flag').validity.valid

    if (!(v1 && v2 && v3)) {
        info61.innerText = '有必填项未填'
    } else {
        const data = new FormData(dept_form);
        axios.post('/dept/add', data)
            .then(function (response) {
                if (response.data.result === 'ok') {
                    info61.innerText = '提交成功'
                    setTimeout(to_dept_list, 1500)
                } else {
                    console.log(response.data.result)
                    info61.innerText = '提交失败'
                }
            })
    }
}

function to_dept_list() {
    window.location.href = '/dept/list/1'
}

function dept_status_switcher(pid) {
    if (window.confirm('确定修改吗？')) {
        const data = {
            "pid": pid,
        }
        axios.post('/dept/status', data, config)
            .then(function (response) {
                if (response.data.result === 'ok') {
                    console.log('操作成功')
                    location.reload()
                } else {
                    console.log('提交失败')
                }
            })
    }
}

function dept_mod(fid){
    window.location.href = '/dept/to_add/' + fid
}