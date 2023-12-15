function paid_cancel(pid) {
    if (window.confirm('确定作废吗？')) {
        const data = {
            "pid": pid,
        }
        axios.post('/paid/cancel', data, config)
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

function fee4_to_audit(pid, fee, filename) {
    $('#pid').val(pid)
    $('#sp_fee').text(fee)
    if (filename === 'None') {
        $('#sp_link').text('无附件')
    } else {
        $('#sp_link').html('<a href="/paid/download?pid=' + pid + '" target="_blank" id="filepath">' + filename + '</a>')
    }
    $("#fee4AuditModal").modal("show")
}

function paid_audit() {
    const data = {
        "pid": $('#pid').val(),
        "status": $('#status').val()
    }
    axios.post('/paid/audit', data, config)
        .then(function (response) {
            if (response.data.result === 'ok') {
                document.getElementById('info41').innerText = '提交成功'
                setTimeout(paid_audit_hide, 1500)
                document.getElementById('paid_form_audit').reset()
                location.reload()
            } else {
                console.log('提交失败')
            }
        })
}

function paid_audit_hide() {
    $("#fee4AuditModal").modal("hide")
}

function paid_mod(fid) {
    window.location.href = '/paid/to_add/' + fid
}

function paid_query(){
    window.location.href = '/paid/list/1/'
}