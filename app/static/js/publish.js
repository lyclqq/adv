function publish_cancel(pid) {
    if (window.confirm('确定作废吗？')) {
        const data = {
            "pid": pid,
        }
        axios.post('/publish/cancel', data, config)
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

function fee2_to_audit(pid, fee, money, filename) {
    $('#pid').val(pid)
    $('#sp_fee').text(fee)
    $('#sp_money').text(money)
    if (filename === 'None') {
        $('#sp_link').text('无附件')
    } else {
        $('#sp_link').html('<a href="/publish/download?pid=' + pid + '" target="_blank" id="filepath">' + filename + '</a>')
    }
    $("#fee2AuditModal").modal("show")
}

function publish_audit() {
    const data = {
        "pid": $('#pid').val(),
        "status": $('#status').val()
    }
    axios.post('/publish/audit', data, config)
        .then(function (response) {
            if (response.data.result === 'ok') {
                document.getElementById('async-info3').innerText = '提交成功'
                document.getElementById('publish_form_audit').reset()
                setTimeout(pub_audit_hide, 1500)
                location.reload()
            } else {
                console.log('提交失败')
            }
        })
}

function pub_audit_hide() {
    $("#fee2AuditModal").modal("hide")
}

function publish_query() {
    window.location.href = '/publish/list/1/'
}

function publish_mod(fid) {
    window.location.href = '/publish/to_add/' + fid
}