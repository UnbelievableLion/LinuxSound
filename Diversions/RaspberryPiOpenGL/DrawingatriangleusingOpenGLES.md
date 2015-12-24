
##  Drawing a triangle using OpenGL ES 


The previous example did the absolute minimum of OpenGL calls,
      just clearing the background. In this setion we do a bit more,
      by using OpenGL calls to clear the background and repeatedly
      draw a triangle (the same one!) multiple times a second.
      The code is just adapted from Chapter 2 of the [
	OpenGL ES 2.0 Programming Guide
      ](http://opengles-book.com/es2/index.html) 


The essential differences from the Programming Guide are

+ We don't give any explanations of the OpenGL code -
	  the Guide has an exhaustive description
+ They hide the grubby details of building OpenGL programs
	  in OS-specific modules such as `esUtils.c`,
	  while we explicitly show the RPi stuff here

The program is [triangle.c](triangle.c) :

```

	
/*
 * code stolen from openGL-RPi-tutorial-master/encode_OGL/
 * and from OpenGLÂ® ES 2.0 Programming Guide
 */

#include <stdio.h>
#include <assert.h>
#include <math.h>
#include <sys/time.h>

#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>

typedef struct CUBE_STATE_T
{
    uint32_t width;
    uint32_t height;

    EGLDisplay display;
    EGLSurface surface;
    EGLContext context;

    EGL_DISPMANX_WINDOW_T nativewindow;
    void *user_data;
    void (*draw_func) (struct CUBE_STATE_T* );
} CUBE_STATE_T;

// from esUtil.h
#define TRUE 1
#define FALSE 0

typedef struct
{
    // Handle to a program object
    GLuint programObject;
} UserData;

///
// Create a shader object, load the shader source, and
// compile the shader.
//
GLuint LoadShader(GLenum type, const char *shaderSrc)
{
    GLuint shader;
    GLint compiled;
    // Create the shader object
    shader = glCreateShader(type);
    if(shader == 0)
	return 0;
    // Load the shader source
    glShaderSource(shader, 1, &shaderSrc, NULL);
    // Compile the shader
    glCompileShader(shader);
    // Check the compile status
    glGetShaderiv(shader, GL_COMPILE_STATUS, &compiled);
    if(!compiled)
	{
	    GLint infoLen = 0;
	    glGetShaderiv(shader, GL_INFO_LOG_LENGTH, &infoLen);
	    if(infoLen > 1)
		{
		    char* infoLog = malloc(sizeof(char) * infoLen);
		    glGetShaderInfoLog(shader, infoLen, NULL, infoLog);
		    fprintf(stderr, "Error compiling shader:\n%s\n", infoLog);
		    free(infoLog);
		}
	    glDeleteShader(shader);
	    return 0;
	}
    return shader;
}
///
// Initialize the shader and program object
//
int Init(CUBE_STATE_T *p_state)
{
    UserData *user_data = p_state->user_data;
    GLbyte vShaderStr[] =
	"attribute vec4 vPosition;\n"
	"void main()\n"
	"{\n"
	"gl_Position = vPosition; \n"
	"}\n";
    GLbyte fShaderStr[] =
	"precision mediump float;\n"
	"void main()\n"
	"{\n"
	" gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); \n"
	"}\n";
    GLuint vertexShader;
    GLuint fragmentShader;
    GLuint programObject;
    GLint linked;

    // Load the vertex/fragment shaders
    vertexShader = LoadShader(GL_VERTEX_SHADER, vShaderStr);
    fragmentShader = LoadShader(GL_FRAGMENT_SHADER, fShaderStr);
    // Create the program object
    programObject = glCreateProgram();
    if(programObject == 0)
	return 0;
    glAttachShader(programObject, vertexShader);
    glAttachShader(programObject, fragmentShader);
    // Bind vPosition to attribute 0
    glBindAttribLocation(programObject, 0, "vPosition");
    // Link the program
    glLinkProgram(programObject);
    // Check the link status
    glGetProgramiv(programObject, GL_LINK_STATUS, &linked);
    if(!linked)
	{
	    GLint infoLen = 0;
	    glGetProgramiv(programObject, GL_INFO_LOG_LENGTH, &infoLen);
	    if(infoLen > 1)
		{
		    char* infoLog = malloc(sizeof(char) * infoLen);
		    glGetProgramInfoLog(programObject, infoLen, NULL, infoLog);
		    fprintf(stderr, "Error linking program:\n%s\n", infoLog);
		    free(infoLog);
		}
	    glDeleteProgram(programObject);
	    return FALSE;
	}
    // Store the program object
    user_data->programObject = programObject;
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    return TRUE;
}

///
// Draw a triangle using the shader pair created in Init()
//
void Draw(CUBE_STATE_T *p_state)
{
    UserData *user_data = p_state->user_data;
    GLfloat vVertices[] = {0.0f, 0.5f, 0.0f,
			   -0.5f, -0.5f, 0.0f,
			   0.5f, -0.5f, 0.0f};
    // Set the viewport
    glViewport(0, 0, p_state->width, p_state->height);
    // Clear the color buffer
    glClear(GL_COLOR_BUFFER_BIT);
    // Use the program object
    glUseProgram(user_data->programObject);
    // Load the vertex data
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, vVertices);
    glEnableVertexAttribArray(0);
    glDrawArrays(GL_TRIANGLES, 0, 3);
    eglSwapBuffers(p_state->display, p_state->surface);
}


CUBE_STATE_T state, *p_state = &state;

void init_ogl(CUBE_STATE_T *state, int width, int height)
{
    int32_t success = 0;
    EGLBoolean result;
    EGLint num_config;

    bcm_host_init();

    DISPMANX_ELEMENT_HANDLE_T dispman_element;
    DISPMANX_DISPLAY_HANDLE_T dispman_display;
    DISPMANX_UPDATE_HANDLE_T dispman_update;
    VC_RECT_T dst_rect;
    VC_RECT_T src_rect;

    static const EGLint attribute_list[] =
	{
	    EGL_RED_SIZE, 8,
	    EGL_GREEN_SIZE, 8,
	    EGL_BLUE_SIZE, 8,
	    EGL_ALPHA_SIZE, 8,
	    EGL_SURFACE_TYPE, EGL_WINDOW_BIT,
	    EGL_NONE
	};

    static const EGLint context_attributes[] =
	{
	    EGL_CONTEXT_CLIENT_VERSION, 2,
	    EGL_NONE
	};

    EGLConfig config;

    // get an EGL display connection
    state->display = eglGetDisplay(EGL_DEFAULT_DISPLAY);

    // initialize the EGL display connection
    result = eglInitialize(state->display, NULL, NULL);

    // get an appropriate EGL frame buffer configuration
    result = eglChooseConfig(state->display, attribute_list, &config, 1, &num_config);
    assert(EGL_FALSE != result);

    // get an appropriate EGL frame buffer configuration
    result = eglBindAPI(EGL_OPENGL_ES_API);
    assert(EGL_FALSE != result);


    // create an EGL rendering context
    state->context = eglCreateContext(state->display, config, EGL_NO_CONTEXT, context_attributes);
    assert(state->context!=EGL_NO_CONTEXT);

    // create an EGL window surface
    success = graphics_get_display_size(0 /* LCD */, &state->width, &state->height);
    assert( success >= 0 );

    state->width = width;
    state->height = height;

    dst_rect.x = 0;
    dst_rect.y = 0;
    dst_rect.width = state->width;
    dst_rect.height = state->height;

    src_rect.x = 0;
    src_rect.y = 0;
    src_rect.width = state->width << 16;
    src_rect.height = state->height << 16;        

    dispman_display = vc_dispmanx_display_open( 0 /* LCD */);
    dispman_update = vc_dispmanx_update_start( 0 );

    dispman_element = 
	vc_dispmanx_element_add(dispman_update, dispman_display,
				0/*layer*/, &dst_rect, 0/*src*/,
				&src_rect, DISPMANX_PROTECTION_NONE, 
				0 /*alpha*/, 0/*clamp*/, 0/*transform*/);

    state->nativewindow.element = dispman_element;
    state->nativewindow.width = state->width;
    state->nativewindow.height = state->height;
    vc_dispmanx_update_submit_sync( dispman_update );

    state->surface = eglCreateWindowSurface( state->display, config, &(state->nativewindow), NULL );
    assert(state->surface != EGL_NO_SURFACE);

    // connect the context to the surface
    result = eglMakeCurrent(state->display, state->surface, state->surface, state->context);
    assert(EGL_FALSE != result);
}

void esInitContext ( CUBE_STATE_T *p_state )
{
   if ( p_state != NULL )
   {
      memset( p_state, 0, sizeof( CUBE_STATE_T) );
   }
}

void esRegisterDrawFunc(CUBE_STATE_T *p_state, void (*draw_func) (CUBE_STATE_T* ) )
{
   p_state->draw_func = draw_func;
}

void  esMainLoop (CUBE_STATE_T *esContext )
{
    struct timeval t1, t2;
    struct timezone tz;
    float deltatime;
    float totaltime = 0.0f;
    unsigned int frames = 0;

    gettimeofday ( &t1 , &tz );

    while(1)
    {
        gettimeofday(&t2, &tz);
        deltatime = (float)(t2.tv_sec - t1.tv_sec + (t2.tv_usec - t1.tv_usec) * 1e-6);
        t1 = t2;

        if (esContext->draw_func != NULL)
            esContext->draw_func(esContext);

        eglSwapBuffers(esContext->display, esContext->surface);

        totaltime += deltatime;
        frames++;
        if (totaltime >  2.0f)
        {
            printf("%4d frames rendered in %1.4f seconds -> FPS=%3.4f\n", frames, totaltime, frames/totaltime);
            totaltime -= 2.0f;
            frames = 0;
        }
    }
}

int main(int argc, char *argv[])
{
    UserData user_data;

    bcm_host_init();
    esInitContext(p_state);
    init_ogl(p_state, 320, 240);

    p_state->user_data = &user_data;

    if(!Init(p_state))
	return 0;
    esRegisterDrawFunc(p_state, Draw);

    eglSwapBuffers(p_state->display, p_state->surface);
    esMainLoop(p_state);
}

      
```
