function user_mod(fid) {
    window.location.href = '/user/to_add/' + fid
}


function user_status_switcher(pid) {
    if (window.confirm('确定修改吗？')) {
        const data = {
            "pid": pid,
        }
        axios.post('/user/status', data, config)
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

function user_add() {
    const info71 = document.getElementById('info71')
    info71.innerText = ''
    const user_form = document.getElementById('user_form')

    const v1 = document.getElementById('username').validity.valid
    const v2 = document.getElementById('type').validity.valid
    const v4 = document.getElementById('group_id').validity.valid

    const obj_pwd = document.getElementById('passwd')
    let flag = true
    if (obj_pwd == null) {
        flag = v1 && v2 && v4
    } else {
        const v3 = document.getElementById('passwd').validity.valid
        flag = v1 && v2 && v3 && v4
    }
    if (!flag) {
        info71.innerText = '有必填项未填'
    } else {
        const data = new FormData(user_form);
        axios.post('/user/add', data)
            .then(function (response) {
                if (response.data.result === 'ok') {
                    info71.innerText = '提交成功'
                    setTimeout(to_user_list, 1500)
                } else {
                    console.log(response.data.result)
                    info71.innerText = '提交失败'
                }
            })
    }
}

function to_user_list() {
    window.location.href = '/user/list/1'
}

function to_reset(uid) {
    const info70 = document.getElementById("info70")
    info70.innerText = ''
    $('#uid').val(uid)
    $('#reset_new').val('')
    $("#resetPwdModal").modal("show")
}

function pwd_reset() {
    const info70 = document.getElementById("info70")
    const v1 = document.getElementById('reset_new').validity.valid
    if (!v1) {
        info70.innerText = '有必填项未填'
    } else {
        const data = new FormData(document.getElementById('pwd_reset_form'));
        axios.post('/user/reset_pwd', data, config)
            .then(function (response) {
                if (response.data.result === 'ok') {
                    info70.innerText = '修改成功'
                    setTimeout(reset_modal_hide, 1500)
                } else {
                    info70.innerText = '修改失败'
                }
            })
    }
}

function reset_modal_hide() {
    $("#resetPwdModal").modal("hide")
}