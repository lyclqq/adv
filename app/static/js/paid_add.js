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

function paid_add() {
    const info40 = document.getElementById('info40')
    info40.innerText = ''
    const paid_form = document.getElementById('paid_form')

    const v1 = document.getElementById('autoComplete').validity.valid
    const v2 = document.getElementById('fee').validity.valid
    const v3 = document.getElementById('feedate').validity.valid

    if (!(v1 && v2 && v3)) {
        info40.innerText = '有必填项未填'
    } else {
        const data = new FormData(paid_form);
        axios.post('/paid/add', data)
            .then(function (response) {
                if (response.data.result === 'ok') {
                    info40.innerText = '提交成功'
                    setTimeout(to_paid_list, 1500)
                } else {
                    console.log(response.data.result)
                    info40.innerText = '提交失败'
                }
            })
    }
}

function to_paid_list() {
    window.location.href = '/paid/list/1'
}