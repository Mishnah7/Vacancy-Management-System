(function ($) {
    "use strict"; // Start of use strict

    // Init editor
    const editor = grapesjs.init({
        container: '#gjs',
        height: '100vh',
        width: 'auto',
        protectedCss: `body{ font-family: sans-serif; max-width: 210mm;height:auto;margin: 20px auto;background: #fff;box-shadow: 0 3px 1px -2px rgba(0,0,0,.2), 0 2px 2px 0 rgba(0,0,0,.14), 0 1px 5px 0 rgba(0,0,0,.12);}`,
        noticeOnUnload: true,
        storageManager: {
            type: 'remote',
            autosave: true,
            stepsBeforeSave: 1,
            urlStore: '/resume/save/',
            urlLoad: '/resume/load/',
            params: { resume_id: resumeId },
            headers: {
                'X-CSRFToken': csrfToken
            },
            onComplete: (jqXHR, status) => {
                // this.style = jqXHR['gjs-css'];
                // $('iframe').load(function () {
                //     $('iframe').contents().find("head")
                //         .append($(`<style type='text/css'>${jqXHR['gjs-css']}</style>`));
                // });
                // let head = document.head;
                // let style = document.createElement('style');
                // head.appendChild(style);
                // style.type = 'text/css';
                // if (style.styleSheet) {
                //     // This is required for IE8 and below.
                //     style.styleSheet.cssText = jqXHR['gjs-css'];
                // } else {
                //     style.appendChild(document.createTextNode(jqXHR['gjs-css']));
                // }
            },
        },
        deviceManager: {
            devices: [{
                name: 'Desktop',
                width: '',
            }, {
                name: 'Mobile',
                width: '320px',
                widthMedia: '480px',
            }]
        },
        assetManager: {
            upload: false,
            dropzone: false
        },
        styleManager: {
            clearProperties: true,
        },
        cssIcons: null,
        fromElement: true,
        plugins: ['gjs-preset-webpage'],
        pluginsOpts: {
            'gjs-preset-webpage': {},
        },
        canvas: {
            styles: [
                'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
                '/static/css/template.css'
            ]
        },
        blockManager: {
            appendTo: '#blocks',
            blocks: [
                {
                    id: 'section',
                    label: 'Section',
                    category: 'Basic',
                    content: `<section class="section">
                        <h2 class="section-title">Section Title</h2>
                        <div class="section-content"></div>
                    </section>`,
                },
                {
                    id: 'experience',
                    label: 'Experience',
                    category: 'Resume',
                    content: `<div class="experience-item">
                        <h3 class="job-title">Job Title</h3>
                        <div class="company">Company Name</div>
                        <div class="period">Period</div>
                        <div class="description">Job description goes here</div>
                    </div>`,
                }
            ]
        }
    });
    // End Init editor

    // Editor load
    editor.on('load', function () {
        // Customize builder interface
        // remove class's state-hover,click...
        var class_state = document.getElementById("gjs-clm-up");
        if (class_state) class_state.remove();
        // add default css on template font-awesome
        const head = editor.Canvas.getDocument().head;
        head.insertAdjacentHTML('beforeend', `<link rel="stylesheet" href="${url_default_css_template}">`);
        // End Customize

        // Edit with ID builder
        // Make private already inserted selectors
        editor.SelectorManager.getAll().each(selector => selector.set('private', 1));

        // All new selectors will be private
        editor.on('selector:add', selector => selector.set('private', 1));
        // End edit with ID builder

        // All Font family setup
        const bodyCSSRule = editor.CssComposer.getRule('#resumecv-layout', {
            atRuleType: 'font-family',
        });
        var bodyFont = '';
        if (bodyCSSRule)
            bodyFont = bodyCSSRule.attributes.style['font-family'];

        var option_fonts = "";
        all_fonts.forEach(function (item) {
            if (bodyFont) {
                if (bodyFont.includes(item))
                    option_fonts += `<option value="${item}" selected>${item}</option>`;
            } else {
                option_fonts += `<option value="${item}">${item}</option>`;
            }

        });

        editor.Panels.addPanel({
            id: 'myNewPanel',
            visible: true,
            content: `
                <div class="left-panel-builder">
                    <label for="font-family">${langs.fontFamily}:</label>
                    <select name="font-family" id="font-family">
                        ${option_fonts}
                    </select>
                    <button id="change_templates" class='btn btn-light'>${langs.changeTemplates}</button>
                    <button id="exportPDF" class='btn btn-success'>${langs.exportPdf}</button>
                </div>`
        });

        $('#font-family').on('change', function () {
            var font = $(this).val();
            var string_font = "'" + font + "'";
            editor.CssComposer.setRule('#resumecv-layout', {
                'font-family': string_font
            });
        });
        // End Font family setup

        // All Button panel
        $("#save-builder").on("click", function (e) {
            editor.store(function (res) {
                var html = "";
                if ($.isEmptyObject(res.error)) {
                    html = '<i class="fa fa-check-circle text-success"></i><small> ' + res.success + '</smal>';
                } else {
                    html = '<i class="fa fa-times-circle text-error"></i><small> ' + res.error + '</smal>';
                }
                Swal.fire({
                    position: 'top-end',
                    timer: 3000,
                    toast: true,
                    html: html,
                    showConfirmButton: false,
                });
            });
        });

        $("#back-button").on("click", function (e) {
            window.location.href = back_button_url;
        });
        $("#exportPDF").on("click", function (e) {
            window.location.href = exportPDF_url;
        });

        // End all button panel event

        //Change templates event
        $('#change_templates').on('click', function () {
            modal.style.display = "block";
        });
        $('.card-template').on('click', function () {
            var templateid = $(this).attr("data-templateid");
            if (templateid) {
                $.ajax({
                    type: "POST",
                    url: url_load_template + "/" + templateid,
                    data: {
                        templateid: templateid,
                        "_token": _token
                    },
                    beforeSend: function () {
                        $('#loadingMessage').css('display', 'block');

                    },
                    success: function (response) {
                        editor.setComponents(response.content);
                        editor.setStyle(response.style);
                        $('#loadingMessage').css('display', 'none');
                        modal.style.display = "none";
                    }
                });
            }
        });
        // End Change templates event
        // Upload image
        editor.on('asset:remove', (response) => {
            var src = response.get('src');
            var data = {
                _token: _token,
                image_src: src
            };
            $.ajax({
                url: url_delete_image,
                type: 'POST',
                data: data,
            });
        });
        editor.on('asset:upload:response', (response) => {
            if (response.error !== undefined) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    html: response.error,
                });

            } else {
                editor.AssetManager.add(response);
            }

        });
        // End upload image

        // Auto-save when components are updated
        editor.on('component:update', () => {
            editor.store();
        });

    });
    // End Editor load

    editor.on('storage:end:load', (e) => {
        $('#loadingMessage').css('display', 'none');
    });

    // Change template event
    var modal = document.getElementById("myModal");
    $('span.close').on('click', function () {
        modal.style.display = "none";
    });

    window.onclick = function (event) {
        if (event.target == modal)
            modal.style.display = "none";
    }
    if ($(window).width() <= 768) {
        $('#loadingMessage').css('display', 'none');
        $('#mobileAlert').css('display', 'block');
    }
    // End Change template

    // Handle font changes
    document.getElementById('font-select').addEventListener('change', (e) => {
        const selectedFont = e.target.value;
        editor.setStyle({
            'font-family': selectedFont
        });
    });

    // Handle device preview
    const deviceButtons = document.querySelectorAll('.device-button');
    deviceButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const device = btn.getAttribute('data-device');
            editor.setDevice(device);
        });
    });

    // Handle template selection
    document.querySelectorAll('.template-select').forEach(btn => {
        btn.addEventListener('click', async () => {
            const templateId = btn.getAttribute('data-template-id');
            try {
                const response = await fetch(`/resume/template/${templateId}/`);
                const template = await response.json();
                editor.setComponents(template.content);
                editor.setStyle(template.style);
            } catch (error) {
                console.error('Error loading template:', error);
            }
        });
    });

    // Show mobile warning on small screens
    function checkMobileWarning() {
        const warning = document.querySelector('.mobile-warning');
        if (window.innerWidth <= 768) {
            warning.style.display = 'block';
        } else {
            warning.style.display = 'none';
        }
    }

    window.addEventListener('resize', checkMobileWarning);
    checkMobileWarning();

})(jQuery); // End of use strict