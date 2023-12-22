const input_auto = 'autoComplete'
const input_hidden = 'order_id'
const tip = ''


const data_src = $('#hidden_names').val().substring(1).split(',')
const idx = $('#hidden_ids').val().substring(1).split(',')

const autoCompleteJS = new autoComplete({
    selector: "#" + input_auto,
    placeHolder: tip,
    data: {
        src: data_src,
        cache: false,
    },
    idx: idx,
    resultsList: {
        element: (list, data) => {
            if (!data.results.length) {
                const message = document.createElement("div");
                message.setAttribute("class", "no_result");
                message.innerHTML = `<span>没找到包含 "${data.query} 的相关数据"</span>`;
                list.prepend(message);
            }
        },
        noResults: true,
    },
    resultItem: {
        highlight: true
    },
    events: {
        input: {
            selection: (event) => {
                const selection = event.detail.selection.value;
                autoCompleteJS.input.value = selection;
                document.getElementById(input_hidden).value = autoCompleteJS.idx[autoCompleteJS.data.src.indexOf(selection)]
            }
        }
    }
});


function perf_add() {
    const info51 = document.getElementById('info51')
    info51.innerText = ''
    const perf_form = document.getElementById('perf_form')

    const v1 = document.getElementById('autoComplete').validity.valid
    const v2 = document.getElementById('fee').validity.valid
    const v3 = document.getElementById('feedate').validity.valid
    const v4 = document.getElementById('prize').validity.valid

    if (!(v1 && v2 && v3 && v4)) {
        info51.innerText = '有必填项未填'
    } else {
        const data = new FormData(perf_form);
        axios.post('/perf/add', data)
            .then(function (response) {
                if (response.data.result === 'ok') {
                    info51.innerText = '提交成功'
                    setTimeout(to_perf_list, 1500)
                } else {
                    console.log(response.data.result)
                    info51.innerText = '提交失败'
                }
            })
    }
}

function to_perf_list() {
    window.location.href = '/perf/list/1'
}