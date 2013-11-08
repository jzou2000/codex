#include <iostream>
#include <xcb/xcb.h>
#include <unistd.h>

using namespace std;

int main(void);
void xdpyinfo(xcb_connection_t *c);

int
main(void)
{
    xcb_connection_t *conn = xcb_connect(NULL, NULL);
    xdpyinfo(conn);

    const xcb_setup_t *setup = xcb_get_setup(conn);
    xcb_screen_t *scr = xcb_setup_roots_iterator(setup).data;
    xcb_window_t wid = xcb_generate_id(conn);

    uint32_t mask = XCB_CW_BACK_PIXEL | XCB_CW_EVENT_MASK;
    uint32_t values[2];
    values[0] = scr->black_pixel;
    values[1] = XCB_EVENT_MASK_BUTTON_PRESS | XCB_EVENT_MASK_EXPOSURE;
    xcb_create_window(conn,
            XCB_COPY_FROM_PARENT, wid, scr->root,
            0, 0, 640, 480, 0,
            XCB_WINDOW_CLASS_INPUT_OUTPUT,  scr->root_visual,
            mask, values);
    xcb_map_window(conn, wid);

    xcb_flush(conn);

    xcb_atom_t atom = (xcb_atom_t) 67;
    xcb_get_atom_name_cookie_t cookie = 
        xcb_get_atom_name(conn, atom);

    /* later ... */
    xcb_generic_error_t *e = NULL;
    xcb_get_atom_name_reply_t *reply =
        xcb_get_atom_name_reply(conn, cookie, &e);
    char* atom_name =
        xcb_get_atom_name_name(reply);
    int len =
        xcb_get_atom_name_name_length(reply);
    string an = string(atom_name, len);
    cout << "atom(" << atom << ")=" << an << endl;
    free(reply);
    


    xcb_generic_event_t *ge;
    bool end = false;
    while (!end && (ge = xcb_wait_for_event(conn))) {
        switch (ge->response_type & ~0x80) {
            case XCB_EXPOSE:
                { xcb_expose_event_t* e = (xcb_expose_event_t*)ge;
                    cout << "event: expose" << endl
                         << "    " << hex << e->window << dec
                         << "  (" << e->x << ","
                         << e->y << ") "
                         << e->width << "x" << e->height
                         << "  count=" << e->count
                         << endl;
                }
                break;
            case XCB_BUTTON_PRESS:
                { xcb_button_press_event_t* e = (xcb_button_press_event_t*)ge;
                    cout << "event: button press" << endl
                         << "    " << hex << e->event
                         << "  (" << dec << e->event_x << ","
                         << e->event_y << ") "
                         << " detail=" << (int) e->detail
                         << " state=" << hex << e->state << dec
                         << endl;
                    if (e->detail == 3)
                        end = true;
                }
                break;
            default:    // ignore unknown event
                break;
        }
        free(ge);
    }

    return 0;
}


void
xdpyinfo(xcb_connection_t *c)
{
    xcb_screen_t        *screen;
    xcb_screen_iterator_t iter;

    iter = xcb_setup_roots_iterator(xcb_get_setup(c));
    for (; iter.rem; xcb_screen_next(&iter)) {
        screen = iter.data;
        cout << endl
             << "screen " << hex << screen->root << dec << endl
             << "    width    " << screen->width_in_pixels << endl
             << "    height   " << screen->height_in_pixels << endl
             << "    white    " << hex << screen->white_pixel << endl
             << "    black    " << screen->black_pixel << endl
             << endl;
    }
}


