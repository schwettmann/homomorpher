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

    const api = new API('http://169.63.46.227/frankenstein/');

    let all_images_apply = [];
    let all_images_train: { z: number[]; image: string }[] = [];

    const update_all_transitions = () => {
        api.all_transitions().then(tr => {
            const selector = d3.select('#sel_transition');
            update_selector(selector,
                tr.map(d => d.descr), tr.map(d => d.id), 'SVM_summerlake')

            selector_on_change_or_enter(selector, () => {
                console.log("-hen--", selector.property('value'))
            })
        })
    }
    update_all_transitions();

    api.all_categories().then(cats => {
        const selector = d3.select('#sel_category');
        update_selector(selector,
            cats.map(cat => cat[0].substr(3)),
            cats.map(cat => cat[1]),
            null)

        selector_on_change_or_enter(selector, () => {
            console.log("-hen--", selector.property('value'))
        })

        const train_selector = d3.select('#train_sel_category');
        update_selector(train_selector,
            cats.map(cat => cat[0].substr(3)),
            cats.map(cat => cat[1]),
            null)

        selector_on_change_or_enter(train_selector, () => {
            console.log("-hen--", train_selector.property('value'))
        })


    })

    const render_apply = () => {

        d3.select("#main").selectAll('.result')
            .data(all_images_apply, (d: { in: string, out: string }) => d.in)
            .join('div')
            .attr('class', 'result col-md-6 col-sm-12 ')
            .html(d => `<div class="row" style="margin-bottom: 10px;">
                    <img src="${d.in}" alt="x" class="col-6"/> 
                    <img src="${d.out}" alt="y" class="col-6">
                    </div>
            `)
    }


    const render_train = () => {
        d3.select("#train_main").selectAll('.result')
            .data(all_images_train)
            .join('div')
            .attr('class', 'result col-lg-2 col-md-3 col-sm-6 ')
            .html(d => `<img src="${d.image}" class="img-fluid"/>`)
            .on('click', function () {
                const me = d3.select(this);
                const selection = d3.event.altKey ? 'to' : 'from';
                const non_selection = selection === 'to' ? 'from' : 'to';
                if (me.classed('select_' + selection)) {
                    me.classed('select_' + selection, null)
                } else {
                    me.classed('select_' + non_selection, null)
                    me.classed('select_' + selection, true)
                }
                check_train_btn()

            })

    }

    const check_train_btn = () => {
        const from_samples_size = d3.select("#train_main").selectAll('.select_from').size();
        const to_samples_size = d3.select("#train_main").selectAll('.select_to').size();

        if (from_samples_size > 4 && to_samples_size > 4) {
            d3.select("#train_btn").attr('disabled', null);
        } else {
            d3.select("#train_btn").attr('disabled', true);
        }

    }

    d3.select("#train_btn").on('click', () => {
        const from_samples: any[] = d3.select("#train_main").selectAll('.select_from').data();
        const to_samples: any[] = d3.select("#train_main").selectAll('.select_to').data();
        let transition_descr = d3.select('#train_name').property('value');
        if (transition_descr.length === 0) transition_descr = null;
        d3.select("#train_btn").attr('disabled', true);
        d3.select("#train_main").html('training....');
        api.learn(from_samples.map(d => d.z), to_samples.map(d => d.z), transition_descr)
            .then(learned => {
                d3.select("#train_main").html(`<div class="result text-light" >${JSON.stringify(learned.result)}</div>`);
                console.log(learned.result, "--- ");
                update_all_transitions();
            })

    })


    d3.select('#gen_btn').on('click', () => {
        const category: number = d3.select('#sel_category').property('value');
        const transitionID = d3.select('#sel_transition').property('value');
        const iter = d3.select('#sel_iter').property('value');

        all_images_apply = [];

        for (let i in d3.range(iter)) {
            api.random_z().then(zs => {
                console.log(zs, "--- zs");
                api.transformImg(category, zs[0], transitionID).then(res => {
                    all_images_apply.push(res.res)
                    render_apply();
                })
            })
        }

    })

    d3.select('#train_gen_btn').on('click', () => {
        const category: number = d3.select('#train_sel_category').property('value');
        const nr_samples = d3.select('#train_sel_samples').property('value');
        api.random_images(nr_samples, category).then(rand_imgs => {
            all_images_train = rand_imgs;
            render_train();
        })

    })

    d3.select('#mode_apply_btn').on('click', () => {
        d3.selectAll('.mode_apply').classed('hide', null);
        d3.selectAll('.mode_train').classed('hide', true);
        d3.select('#mode_apply_btn').attr('class', 'btn btn-light');
        d3.select('#mode_train_btn').attr('class', 'btn btn-dark');
    })

    d3.select('#mode_train_btn').on('click', () => {
        d3.selectAll('.mode_train').classed('hide', null);
        d3.selectAll('.mode_apply').classed('hide', true);
        d3.select('#mode_train_btn').attr('class', 'btn btn-light');
        d3.select('#mode_apply_btn').attr('class', 'btn btn-dark');
    })


    /**
     * Binding the event handler
     */
    eventHandler.bind(HTMLList.events.click, (d) => console.log(`${d.s} was clicked!`))

    // wl.update(data)
}
