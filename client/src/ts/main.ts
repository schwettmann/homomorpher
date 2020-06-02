import * as d3 from 'd3'
import {HTMLList, SVGList} from './vis/ExampleComponent'
import {SimpleEventHandler} from './etc/SimpleEventHandler'
import {API} from "./api/mainApi";
import {selector_on_change_or_enter, update_selector} from "./etc/Util";

/**
 * Main functionality in the below function
 */
export function main() {
    const eventHandler = new SimpleEventHandler(<Element>d3.select('body').node())

    // const data = ["this", "is", "a", "string", "of", "new", "data"]
    // const mainDiv = document.getElementById('main')
    // const wl = new HTMLList(mainDiv, eventHandler)

    const api = new API('http://ganpaint.io/frankenstein/');

    let all_images = [];


    api.all_transitions().then(tr => {
        const selector = d3.select('#sel_transition');
        update_selector(selector,
            Object.keys(tr).map(k => tr[k]), Object.keys(tr), 'SVM_summerlake')

        selector_on_change_or_enter(selector, () => {
            console.log("-hen--", selector.property('value'))
        })
    })

    api.all_categories().then(cats => {
        const selector = d3.select('#sel_category');
        update_selector(selector,
            cats.map(cat => cat[0].substr(3)),
            cats.map(cat => cat[1]),
            null)

        selector_on_change_or_enter(selector, () => {
            console.log("-hen--", selector.property('value'))
        })
    })

    const re_render = () => {

        d3.select("#main").selectAll('.result')
            .data(all_images, (d: { in: string, out: string }) => d.in)
            .join('div')
            .attr('class', 'result col-md-6 col-sm-12 ')
            .html(d => `<div class="row" style="margin-bottom: 10px;">
                    <img src="${d.in}" alt="x" class="col-6"/> 
                    <img src="${d.out}" alt="y" class="col-6">
                    </div>
            `)


    }


    d3.select('#gen_btn').on('click', () => {
        const category: number = d3.select('#sel_category').property('value');
        const transitionID = d3.select('#sel_transition').property('value');
        const iter = d3.select('#sel_iter').property('value');

        all_images = [];

        for (let i in d3.range(iter)) {
            api.random_z().then(zs => {
                console.log(zs, "--- zs");
                api.transformImg(category, zs[0], transitionID).then(res => {
                    all_images.push(res.res)
                    re_render();
                })
            })
        }

    })


    /**
     * Binding the event handler
     */
    eventHandler.bind(HTMLList.events.click, (d) => console.log(`${d.s} was clicked!`))

    // wl.update(data)
}
