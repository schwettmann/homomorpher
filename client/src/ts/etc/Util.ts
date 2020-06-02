import * as d3 from "d3";
import {BaseType} from "d3";

/**
 * Created by hen on 5/15/17.
 * Modifyed by hoo on 4/16/19.
 */
let the_unique_id_counter = 0;

export class Util {
    static simpleUId({prefix = ''}): string {
        the_unique_id_counter += 1;

        return prefix + the_unique_id_counter;
    }
}

export type D3Sel = d3.Selection<any, any, any, any>

/**
 * Selection utility functions should be static methods in the below class
 */
export class Sel {
    static setSelVisible = (x: D3Sel) => x.attr("visibility", "visible")
    static setSelHidden = (x: D3Sel) => x.attr("visibility", "hidden")
    static setVisible = (x: string) => Sel.setSelVisible(d3.selectAll(x))
    static setHidden = (x: string) => Sel.setSelHidden(d3.selectAll(x))
    static hideElement = (hE: D3Sel) => hE.transition()
        .style('opacity', 0)
        .style('pointer-events', 'none')
        .style('display', 'none')
    static unhideElement = (hE: D3Sel) => hE.transition()
        .style('opacity', 1)
        .style('pointer-events', null)
        .style('display', null)
}

export interface LooseObject {
    [key: string]: any
}

export type d3S<T extends BaseType, U = any> = d3.Selection<T, U, any, any>

export function update_selector(selector, entries, values: (string|number)[] = null, defaultOption: string = null) {
    let rec_op = selector.selectAll('option').data(entries);
    rec_op.join('option')
        .attr('value', (d, i) => values ? values[i] : d)
        .attr('selected', d => d == defaultOption ? true : null)
        .text(d => d);
};


export function selector_on_change_or_enter(selector, f) {
    selector.on('change', () => {
        f();
    });

    selector.on('keypress', () => {
        if (d3.event.keyCode == 13) {
            f();
        }
    });
}
