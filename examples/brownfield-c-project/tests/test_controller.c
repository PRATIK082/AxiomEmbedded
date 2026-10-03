#include "controller.h"
int main(void) {
    return controller_step(1) == 2 ? 0 : 1;
}
