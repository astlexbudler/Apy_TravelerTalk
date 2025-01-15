/**
 * Newzy – Multipurpose Blog Template
 * Copyright 2023 pxdraft
 * Theme core scripts
 * 
 * @author pxdraft
 * @version 1
 */

"use strict";
const d = document;
d.addEventListener("DOMContentLoaded", function(event) {

    // Plceholder
    var preloader = d.querySelector('.loading-preloader');
    if (preloader) {
        setTimeout(function() {
            preloader.classList.add('d-none');
        }, 1000);
    }


    // Tooltips
    var ToolTipTrigger = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = ToolTipTrigger.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // Popovers
    var PopoverTrigger = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = PopoverTrigger.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    })


    // Swiper
    var sliderSelector = '.swiper-container',
        defaultOptions = {
            breakpointsInverse: true,
            observer: true
        };

    var nSlider = document.querySelectorAll(sliderSelector);

    [].forEach.call(nSlider, function(slider, index, arr) {
        var data = slider.getAttribute('data-swiper-options') || {};

        if (data) {
            var dataOptions = JSON.parse(data);
        }

        slider.options = Object.assign({}, defaultOptions, dataOptions);

        var swiper = new Swiper(slider, slider.options);

        //console.log(slider.options.autoplay)

        /* stop on hover */
        if (typeof slider.options.autoplay !== 'undefined' && slider.options.autoplay !== false) {
            slider.addEventListener('mouseenter', function(e) {
                swiper.autoplay.stop();
                //console.log('stop')
            });

            slider.addEventListener('mouseleave', function(e) {
                swiper.autoplay.start();
                //console.log('start')
            });
        }
    });


});