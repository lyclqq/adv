function perf_mod(fid) {
    window.location.href = '/perf/to_add/' + fid
}

function perf_cancel(pid) {
    if (window.confirm('确定作废吗？')) {
        const data = {
            "pid": pid,
        }
        axios.post('/perf/cancel', data, config)
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

function fee5_to_audit(pid, fee, prize) {
    $('#pid').val(pid)
    $('#sp_fee').text(fee)
    $('#sp_prize').text(prize)
    $("#fee5AuditModal").modal("show")
}


function perf_audit() {
    const data = {
        "pid": $('#pid').val(),
        "status": $('#status').val()
    }
    axios.post('/perf/audit', data, config)
        .then(function (response) {
            if (response.data.result === 'ok') {
                document.getElementById('info50').innerText = '提交成功'
                setTimeout(perf_audit_hide, 1500)
                document.getElementById('perf_form_audit').reset()
                location.reload()
            } else {
                console.log('提交失败')
            }
        })
}

function perf_audit_hide() {
    $("#fee5AuditModal").modal("hide")
}

function perf_query(){
    window.location.href = '/perf/list/1/'
}