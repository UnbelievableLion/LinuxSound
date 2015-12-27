
##  Drawing an image using OpenGL ES


The OpenGL ES Programming Guide includes an example of drawing
a simple image using an array of pixels. Realistically, it notes
that the image data is more likely to be read from a file.
In this section we fill in the details.


There are many, many different file formats, some lossy, some lossless,
some compressed, some not, some with metadata, some without.
In this section we just use [TGA](http://www.fileformat.info/format/tga/egff.htm) - an
uncompressed format with enough useful metadata, simple to load.


TGA files can be created from e.g. JPEG files by using the `convert`utility from the Gimp drawing system.
It is simple to convert a file: just give the appropriate
file extensions:

```

	
convert image.jpg image.tga
	
      
```


(Later sections look at decompressing files using the GPU itself.)


A TGA file has a header section which gives the width and height of the
image from which its size can be calculated. The default format will
be RGB, as 24-bit pixels. Reading in such a file is just a matter
of locating the dimensions, malloc'ing the right size buffer,
skipping to the start of the image data and reading it all in.


The default is for the origin of the image to be the bottom lefthand
corner, with the y-axis growing up. OpenGL ES on the other hand
has the origin in the top lefthand corner with the y-axis growing down.
So the image will be upside down. This can be fixed by reading the data
in differently, or by using an OpenGL ES reflection.


Getting a native window is done as before. Using the OpenGL ES Programming
Guide example, we also need to substitute our image array for their
2x2 array, adjusting the image bounds. Apart from those, there is no real
change.
The program is [image.c](image.c) 

```cpp

	
/*
 * code stolen from openGL-RPi-tutorial-master/encode_OGL/
 * and from OpenGLÂ® ES 2.0 Programming Guide
 */

#include <stdio.h>
#include <assert.h>
#include <math.h>
#include <sys/time.h>
//#include "jpeg.h"

#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>


// from esUtil.h
#define TRUE 1
#define FALSE 0

typedef struct
{
    // Handle to a program object
    GLuint programObject;

   // Attribute locations
   GLint  positionLoc;
   GLint  texCoordLoc;

   // Sampler location
   GLint samplerLoc;

   // Texture handle
   GLuint textureId;

} UserData;

typedef struct CUBE_STATE_T
{
    uint32_t width;
    uint32_t height;

    EGLDisplay display;
    EGLSurface surface;
    EGLContext context;

    EGL_DISPMANX_WINDOW_T nativewindow;
    UserData *user_data;
    void (*draw_func) (struct CUBE_STATE_T* );
} CUBE_STATE_T;

char *image;
int tex;


char* esLoadTGA ( char *fileName, int *width, int *height )
{
    char *buffer = NULL;
    FILE *f;
    unsigned char tgaheader[12];
    unsigned char attributes[6];
    unsigned int imagesize;

    f = fopen(fileName, "rb");
    if(f == NULL) return NULL;

    if(fread(&tgaheader, sizeof(tgaheader), 1, f) == 0)
    {
        fclose(f);
        return NULL;
    }

    if(fread(attributes, sizeof(attributes), 1, f) == 0)
    {
        fclose(f);
        return 0;
    }

    *width = attributes[1] * 256 + attributes[0];
    *height = attributes[3] * 256 + attributes[2];
    imagesize = attributes[4] / 8 * *width * *height;
    //imagesize *= 4/3;
    printf("Origin bits: %d\n", attributes[5] & 030);
    printf("Pixel depth %d\n", attributes[4]);
    buffer = malloc(imagesize);
    if (buffer == NULL)
    {
        fclose(f);
        return 0;
    }

#if 1
    // invert - should be reflect, easier is 180 rotate
    int n = 1;
    while (n <= imagesize) {
	fread(&buffer[imagesize - n], 1, 1, f);
	n++;
    }
#else
    // as is - upside down
    if(fread(buffer, 1, imagesize, f) != imagesize)
    {
        free(buffer);
        return NULL;
    }
#endif
    fclose(f);
    return buffer;
}

///
// Create a simple width x height texture image with four different colors
//
GLuint CreateSimpleTexture2D(int width, int height )
{
   // Texture object handle
   GLuint textureId;

   // Use tightly packed data
   glPixelStorei ( GL_UNPACK_ALIGNMENT, 1 );

   // Generate a texture object
   glGenTextures ( 1, &textureId );

   // Bind the texture object
   glBindTexture ( GL_TEXTURE_2D, textureId );

   // Load the texture


   glTexImage2D ( GL_TEXTURE_2D, 0, GL_RGB, 
		  width, height, 
		  0, GL_RGB, GL_UNSIGNED_BYTE, image );

   // Set the filtering mode
   glTexParameteri ( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST );
   glTexParameteri ( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST );
   return textureId;
}



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

GLuint LoadProgram ( const char *vertShaderSrc, const char *fragShaderSrc )
{
   GLuint vertexShader;
   GLuint fragmentShader;
   GLuint programObject;
   GLint linked;

   // Load the vertex/fragment shaders
   vertexShader = LoadShader ( GL_VERTEX_SHADER, vertShaderSrc );
   if ( vertexShader == 0 )
      return 0;

   fragmentShader = LoadShader ( GL_FRAGMENT_SHADER, fragShaderSrc );
   if ( fragmentShader == 0 )
   {
      glDeleteShader( vertexShader );
      return 0;
   }

   // Create the program object
   programObject = glCreateProgram ( );
   
   if ( programObject == 0 )
      return 0;

   glAttachShader ( programObject, vertexShader );
   glAttachShader ( programObject, fragmentShader );

   // Link the program
   glLinkProgram ( programObject );

   // Check the link status
   glGetProgramiv ( programObject, GL_LINK_STATUS, &linked );

   if ( !linked ) 
   {
      GLint infoLen = 0;
      glGetProgramiv ( programObject, GL_INFO_LOG_LENGTH, &infoLen );
      
      if ( infoLen > 1 )
      {
         char* infoLog = malloc (sizeof(char) * infoLen );

         glGetProgramInfoLog ( programObject, infoLen, NULL, infoLog );
         fprintf (stderr, "Error linking program:\n%s\n", infoLog );            
         
         free ( infoLog );
      }

      glDeleteProgram ( programObject );
      return 0;
   }

   // Free up no longer needed shader resources
   glDeleteShader ( vertexShader );
   glDeleteShader ( fragmentShader );

   return programObject;
}

///
// Initialize the shader and program object
//
int Init(CUBE_STATE_T *p_state)
{

   p_state->user_data = malloc(sizeof(UserData));      
   UserData *userData = p_state->user_data;
   GLbyte vShaderStr[] =  
      "attribute vec4 a_position;   \n"
      "attribute vec2 a_texCoord;   \n"
      "varying vec2 v_texCoord;     \n"
      "void main()                  \n"
      "{                            \n"
      "   gl_Position = a_position; \n"
      "   v_texCoord = a_texCoord;  \n"
      "}                            \n";
   
   GLbyte fShaderStr[] =  
      "precision mediump float;                            \n"
      "varying vec2 v_texCoord;                            \n"
      "uniform sampler2D s_texture;                        \n"
      "void main()                                         \n"
      "{                                                   \n"
      "  gl_FragColor = texture2D( s_texture, v_texCoord );\n"
      "}                                                   \n";

   // Load the shaders and get a linked program object
   userData->programObject = LoadProgram ( vShaderStr, fShaderStr );

   // Get the attribute locations
   userData->positionLoc = glGetAttribLocation ( userData->programObject, "a_position" );
   userData->texCoordLoc = glGetAttribLocation ( userData->programObject, "a_texCoord" );
   
   // Get the sampler location
   userData->samplerLoc = glGetUniformLocation ( userData->programObject, "s_texture" );
   // Load the texture
   userData->textureId = CreateSimpleTexture2D (p_state->width, p_state->height);

   glClearColor ( 0.0f, 0.0f, 0.0f, 0.0f );
   return GL_TRUE;
}

///
// Draw triangles using the shader pair created in Init()
//
void Draw(CUBE_STATE_T *p_state)
{
   UserData *userData = p_state->user_data;

   GLfloat vVertices[] = { -0.5f,  0.5f, 0.0f,  // Position 0
                            0.0f,  0.0f,        // TexCoord 0 
                           -0.5f, -0.5f, 0.0f,  // Position 1
                            0.0f,  1.0f,        // TexCoord 1
                            0.5f, -0.5f, 0.0f,  // Position 2
                            1.0f,  1.0f,        // TexCoord 2
                            0.5f,  0.5f, 0.0f,  // Position 3
                            1.0f,  0.0f         // TexCoord 3
                         };

   GLushort indices[] = { 0, 1, 2, 0, 2, 3 };
   //GLushort indices[] = {1, 0, 3, 0, 2, 0, 1 };
      
   // Set the viewport
   glViewport ( 0, 0, p_state->width, p_state->height );
   
   // Clear the color buffer
   glClear ( GL_COLOR_BUFFER_BIT );

   // Use the program object
   glUseProgram ( userData->programObject );

   // Load the vertex position
   glVertexAttribPointer ( userData->positionLoc, 3, GL_FLOAT, 
                           GL_FALSE, 5 * sizeof(GLfloat), vVertices );
   // Load the texture coordinate
   glVertexAttribPointer ( userData->texCoordLoc, 2, GL_FLOAT,
                           GL_FALSE, 5 * sizeof(GLfloat), &vVertices[3] );

   glEnableVertexAttribArray ( userData->positionLoc );
   glEnableVertexAttribArray ( userData->texCoordLoc );

   // Bind the texture
   glActiveTexture ( GL_TEXTURE0 );
   glBindTexture ( GL_TEXTURE_2D, userData->textureId );

   // Set the sampler texture unit to 0
   glUniform1i ( userData->samplerLoc, 0 );

   glDrawElements ( GL_TRIANGLES, 6, GL_UNSIGNED_SHORT, indices );
   //glDrawElements ( GL_TRIANGLE_STRIP, 6, GL_UNSIGNED_SHORT, indices );
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
    int width, height;

    image = esLoadTGA("jan.tga", &width, &height);
    if (image == NULL) {
	fprintf(stderr, "No such image\n");
	exit(1);
    }
    fprintf(stderr, "Image is %d x %d\n", width, height);

    bcm_host_init();
    esInitContext(p_state);

    init_ogl(p_state, width, height);

    p_state->user_data = &user_data;
    p_state->width = width;
    p_state->height = height;

    if(!Init(p_state))
	return 0;

    esRegisterDrawFunc(p_state, Draw);

    eglSwapBuffers(p_state->display, p_state->surface);
    esMainLoop(p_state);
}

      
```


The image used is of [me](jan.tga) .

***


Copyright © Jan Newmarch, jan@newmarch.name


<a href="http://creativecommons.org/licenses/by-sa/4.0/" rel="license">
<img alt="Creative Commons License" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" style="border-width:0"/>
</a>


"Programming and Using Linux Sound - in depth"by [Jan Newmarch](https://jan.newmarch.name) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) .


Based on a work at [https://jan.newmarch.name/LinuxSound/](https://jan.newmarch.name/LinuxSound/) .


If you like this book, please contribute using PayPal


<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&amp;business=jan%40newmarch%2ename&amp;lc=AU&amp;item_name=LinuxSound&amp;currency_code=AUD&amp;bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted">
<img src="https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/btn/btn_donateCC_LG.gif"/>
</a>


Or Flattr me:


<a href="https://flattr.com/submit/auto?user_id=jannewmarch&amp;url=http://jan.newmarch.name&amp;title=Linux%20Sound&amp;description=Programming%20and%20Using%20Linu%20Sound&amp;language=en_GB&amp;tags=linux,sound,alsa,pulseaudio,JavaSound,MIDI&amp;category=text">
<img alt="Flattr this book" src="https://api.flattr.com/button/flattr-badge-large.png"/>
</a>
