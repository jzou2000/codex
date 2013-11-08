// g++ gtkmm-hello.cpp -o gtkmm-hello `pkg-config gtkmm-3.0 --cflags --libs`

#include <gtkmm/button.h>
#include <gtkmm/window.h>
//#include <gtkmm.h>
#include <iostream>


class HelloWorld : public Gtk::Window
{
    public:
        HelloWorld();
        virtual ~HelloWorld();

    protected:
        // signal handlers
        void on_button_clicked();

        // contained widgets
        Gtk::Button m_button;
};

HelloWorld::HelloWorld()
    : m_button("Push Me!")
{
    set_border_width(10);
    set_default_size(200, 200);

    m_button.signal_clicked().connect(sigc::mem_fun(*this,
                &HelloWorld::on_button_clicked));

    add(m_button);

    m_button.show();
}

HelloWorld::~HelloWorld()
{
}

void HelloWorld::on_button_clicked()
{
    std::cout << "Hello world: button pressed" << std::endl;
}


int main(int argc, char* argv[])
{
    Glib::RefPtr<Gtk::Application> app = 
        Gtk::Application::create(argc, argv,
                "org.gtkmm.hello");

    HelloWorld helloworld;

    return app->run(helloworld);
}

