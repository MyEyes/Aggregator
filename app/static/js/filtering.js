
function load_filter()
{
    try
    {
        document.filter_obj = JSON.parse($("#filter_info_div")[0].innerText);
        return
    }
    catch{}
    try{
        const urlParams = new URLSearchParams(window.location.search)
        let filter_param = urlParams.get('filter')
        if(filter_param !== null)
        {
            document.filter_obj = JSON.parse(filter_param);
        }
        return;
    }
    catch{}
    document.filter_obj = {}
}

function set_filter(filter_obj)
{
    document.filter_obj = filter_obj
    let urlParams = new URLSearchParams(window.location.search)
    let new_filter = JSON.stringify(document.filter_obj)
    urlParams.set('filter', new_filter)
    window.location.search = urlParams;
}

function pagination_set_page(page)
{
    if(page<0)
        page = 0
    if(!document.filter_obj.pagination)
        document.filter_obj.pagination = {"page": page, "per_page": 20}
    else
        document.filter_obj.pagination.page = page
    refresh_filter()
}

function pagination_get_page()
{
    if(!document.filter_obj.pagination)
        return 1
    else if(!document.filter_obj.pagination.page)
        return 1
    return document.filter_obj.pagination.page
}

function pagination_forward()
{
    pagination_set_page(pagination_get_page()+1)
}

function pagination_backward()
{
    pagination_set_page(pagination_get_page()-1)
}

function set_search_term(term)
{
    document.filter_obj.search = {"term": term}
    refresh_filter()
}

function get_filter_tag_ids()
{
    if(!document.filter_obj.tag_filter)
        return []
    if(!document.filter_obj.tag_filter.tags)
        return []
    return document.filter_obj.tag_filter.tags
}

function set_filter_tag_ids(tag_ids)
{
    document.filter_obj.tag_filter = {"tags": tag_ids}
    refresh_filter()
}

function add_filter_tag(tag_id)
{
    let arr = get_filter_tag_ids()
    arr.push(tag_id)
    set_filter_tag_ids(arr)
}

function remove_filter_tag(tag_id)
{
    let arr = get_filter_tag_ids()
    arr = arr.filter(item => item !== tag_id)
    set_filter_tag_ids(arr)
}

function refresh_filter()
{
    set_filter(document.filter_obj)
}

function search_submit(evt)
{
    console.info("submitted")
    evt.preventDefault();
    set_search_term($('#search-bar-val').val())
}

function get_order_desc()
{
    if(!document.filter_obj)
        return {}
    if(!document.filter_obj.order)
        return {}
    return document.filter_obj.order
}
function set_order_desc(order_desc)
{
    if(!document.filter_obj)
        document.filter_obj = {}
    document.filter_obj.order = order_desc
}

function order_by(sort_criterium)
{
    var sort_desc = get_order_desc()
    sort_desc.order_by = sort_criterium
    set_order_desc(sort_desc)
}

function order_op(op)
{
    var sort_desc = get_order_desc()
    sort_desc.ordering = op
    set_order_desc(sort_desc)
}

function order_click(ev)
{
    var order_by_val = ev.target.id
    var order_op_val = "asc"
    if(ev.target.classList.contains("asc"))
        order_op_val = "desc"
    order_by(order_by_val)
    order_op(order_op_val)
    refresh_filter()
}

function set_up_orders()
{
    $(".order-button").on("click", order_click);
    var order_desc = get_order_desc()
    if(order_desc.order_by)
    {
        if(order_desc.ordering == "asc")
            $(".order-button#"+order_desc.order_by).toggleClass("asc")
        else
            $(".order-button#"+order_desc.order_by).toggleClass("desc")
    }
}

function set_up_search()
{
    /*If there is a search bar hook it up properly*/
    try
    {
        $('#search-bar')[0].addEventListener("submit", search_submit);
    }catch{}
}

load_filter()
//console.info(document.filter_obj)

set_up_search()
set_up_orders()