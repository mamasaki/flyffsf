#ifndef __2DRENDER_H
#define __2DRENDER_H



#ifdef __CLIENT
#include "mempooler.h"
#endif
#ifndef __WORLDSERVER
#include "EditString.h"
#endif	// __CLEINT

#include "..\_UnhandledException\ExceptionHandler.h"
#include "xUtil.h"

struct IDeviceRes
{
	virtual void Invalidate()								 = 0;
	virtual BOOL SetInvalidate(LPDIRECT3DDEVICE9 pd3dDevice) = 0;
};

class CRectClip : public CRect
{
public:
	CRectClip() { }
	CRectClip(int l,int t,int r,int b) : CRect(l,t,r,b) { }
	CRectClip(const RECT& srcRect) : CRect(srcRect) { }
	CRectClip(LPCRECT lpSrcRect) : CRect(lpSrcRect) { }
	CRectClip(POINT point,SIZE size) : CRect(point,size) { }
	CRectClip(POINT topLeft,POINT bottomRight) : CRect(topLeft,bottomRight) { }

	BOOL Clipping(CRect& rect) const;
//BOOL Clipping(CRect& os,Rect& is);

	//BOOL Clipping(CPtSz& os,CPtSz& is) const;

	//BOOL PtSzLapRect(CPtSz ptSz) const;
	//BOOL PtSzInRect (CPtSz ptSz) const;
	BOOL RectLapRect(CRect rect) const;
	BOOL RectInRect (CRect rect) const;
};

#define D2DTEXRENDERFLAG_90    1
#define D2DTEXRENDERFLAG_180   2
#define D2DTEXRENDERFLAG_HFLIP 3
#define D2DTEXRENDERFLAG_VFLIP 4

struct DRAWVERTEX
{
	D3DXVECTOR3 vec;//AT x, y, z;
	FLOAT rhw;
	DWORD color; 
//	FLOAT u, v;
};
struct TEXTUREVERTEX
{
	D3DXVECTOR3 vec;//
	//FLOAT x, y, z, 
	FLOAT rhw, u, v;
};
struct TEXTUREVERTEX2
{
	D3DXVECTOR3 vec;//
	//FLOAT x, y, z, 
	FLOAT rhw;
	DWORD color; 
	FLOAT u, v;
};
#define D3DFVF_DRAWVERTEX (D3DFVF_XYZRHW|D3DFVF_DIFFUSE/*|D3DFVF_TEX1*/)	// FVF가 맞지않아 경고가 떠서 지웠음.-xuzhu-
#define D3DFVF_TEXTUREVERTEX (D3DFVF_XYZRHW|D3DFVF_TEX1)
#define D3DFVF_TEXTUREVERTEX2 (D3DFVF_XYZRHW|D3DFVF_DIFFUSE|D3DFVF_TEX1)

inline void SetDrawVertex( DRAWVERTEX* pVertices, FLOAT x, FLOAT y, DWORD dwColor )
{
	pVertices->vec = D3DXVECTOR3( x,y,0);
	pVertices->rhw   = 1.0f;
	pVertices->color = dwColor;
}
inline void SetTextureVertex( TEXTUREVERTEX* pVertices, FLOAT x, FLOAT y, FLOAT u, FLOAT v )
{
	//pVertices->x     = (FLOAT)x - 0.5f;
	//pVertices->y     = (FLOAT)y - 0.5f;
	//pVertices->z     = 0.0f;
	pVertices->vec = D3DXVECTOR3( x - 0.5f, y - 0.5f, 0 );
	pVertices->rhw   = 1.0f;
	pVertices->u     = u;
	pVertices->v     = v;
}
inline void SetTextureVertex2( TEXTUREVERTEX2* pVertices, FLOAT x, FLOAT y, FLOAT u, FLOAT v, DWORD dwColor )
{
	//pVertices->x     = (FLOAT)x - 0.5f;
	//pVertices->y     = (FLOAT)y - 0.5f;
	//pVertices->z     = 0.0f;
	pVertices->vec = D3DXVECTOR3( x - 0.5f, y - 0.5f, 0 );
	pVertices->rhw   = 1.0f;
	pVertices->u     = u;
	pVertices->v     = v;
	pVertices->color = dwColor;
}

class CTexture;
class CTexturePack;


class C2DRender
{
	LPDIRECT3DVERTEXBUFFER9 m_pVBRect;
	LPDIRECT3DVERTEXBUFFER9 m_pVBFillRect;
	LPDIRECT3DVERTEXBUFFER9 m_pVBRoundRect;
	LPDIRECT3DVERTEXBUFFER9 m_pVBFillTriangle;
	LPDIRECT3DVERTEXBUFFER9 m_pVBTriangle;
	LPDIRECT3DVERTEXBUFFER9 m_pVBLine;
	LPDIRECT3DVERTEXBUFFER9 m_pVBPixel;
	//LPDIRECT3DVERTEXBUFFER9 m_pVBTexture;
	
public:
	LPDIRECT3DDEVICE9 m_pd3dDevice; // The D3D rendering device
	DWORD      m_dwTextColor;
	CD3DFont*  m_pFont;
 	CPoint     m_ptOrigin ; // 뷰포트 시작 지점 
	CRectClip  m_clipRect;

	C2DRender(); 
	~C2DRender();

	CD3DFont* GetFont() { return m_pFont; }
	void SetFont( CD3DFont* pFont ) { m_pFont = pFont; }

	// 뷰포트 관련 
	CPoint GetViewportOrg() const { return m_ptOrigin; }
	void SetViewportOrg(POINT pt) { m_ptOrigin = pt; }
	void SetViewportOrg(int x,int y) { m_ptOrigin = CPoint(x,y); }
	void SetViewport(CRect rect);
	void SetViewport(int nLeft,int nTop,int nRight,int nBottom);

	BOOL ResizeRectVB( CRect* pRect, DWORD dwColorLT, DWORD dwColorRT, DWORD dwColorLB, DWORD dwColorRB, LPDIRECT3DVERTEXBUFFER9 pVB );
	BOOL RenderRect  ( CRect rect, DWORD dwColorLT, DWORD dwColorRT, DWORD dwColorLB, DWORD dwColorRB );
	BOOL RenderRect  ( CRect rect, DWORD dwColor ) { return RenderRect( rect, dwColor, dwColor, dwColor, dwColor); }
	BOOL RenderResizeRect( CRect rect, int nThick );

	BOOL ResizeFillRectVB( CRect* pRect, DWORD dwColorLT, DWORD dwColorRT, DWORD dwColorLB, DWORD dwColorRB, LPDIRECT3DVERTEXBUFFER9 pVB, LPDIRECT3DTEXTURE9 m_pTexture = NULL );
	BOOL RenderFillRect  ( CRect rect, DWORD dwColorLT, DWORD dwColorRT, DWORD dwColorLB, DWORD dwColorRB, LPDIRECT3DTEXTURE9 m_pTexture = NULL );
	BOOL RenderFillRect  ( CRect rect, DWORD dwColor, LPDIRECT3DTEXTURE9 m_pTexture = NULL ) { return RenderFillRect( rect, dwColor, dwColor, dwColor, dwColor, m_pTexture); }

	BOOL ResizeRoundRectVB( CRect* pRect, DWORD dwColorLT, DWORD dwColorRT, DWORD dwColorLB, DWORD dwColorRB, LPDIRECT3DVERTEXBUFFER9 pVB, LPDIRECT3DTEXTURE9 m_pTexture = NULL );
	BOOL RenderRoundRect  ( CRect rect, DWORD dwColorLT, DWORD dwColorRT, DWORD dwColorLB, DWORD dwColorRB, LPDIRECT3DTEXTURE9 m_pTexture = NULL );
	BOOL RenderRoundRect  ( CRect rect, DWORD dwColor, LPDIRECT3DTEXTURE9 m_pTexture = NULL ) { return RenderRoundRect( rect, dwColor, dwColor, dwColor, dwColor, m_pTexture ); }

	BOOL RenderLine( CPoint pt1, CPoint pt2, DWORD dwColor1, DWORD dwColor2 );
	BOOL RenderLine( CPoint pt1, CPoint pt2, DWORD dwColor ) { return RenderLine(pt1,pt2,dwColor,dwColor); }

	BOOL RenderTriangle( CPoint pt1, CPoint pt2, CPoint pt3, DWORD dwColor1, DWORD dwColor2, DWORD dwColor3 );
	BOOL RenderTriangle( CPoint pt1, CPoint pt2, CPoint pt3, DWORD dwColor ) { return RenderTriangle( pt1, pt2, pt3, dwColor, dwColor, dwColor ); }

	BOOL RenderFillTriangle( CPoint pt1, CPoint pt2, CPoint pt3, DWORD dwColor1, DWORD dwColor2, DWORD dwColor3 );
	BOOL RenderFillTriangle( CPoint pt1, CPoint pt2, CPoint pt3, DWORD dwColor ) { return RenderFillTriangle( pt1, pt2, pt3, dwColor, dwColor, dwColor ); }

	BOOL RenderTextureEx( CPoint pt, CPoint pt2, CTexture* pTexture, DWORD dwBlendFactorAlhpa, FLOAT fScaleX , FLOAT fScaleY, BOOL bAnti = TRUE );
	BOOL RenderTexture( CPoint pt, CTexture* pTexture, DWORD dwBlendFactorAlhpa = 255, FLOAT fScaleX=1.0 , FLOAT fScaleY=1.0 );
	BOOL RenderTextureRotate( CPoint pt, CTexture* pTexture, DWORD dwBlendFactorAlhpa, FLOAT fScaleX , FLOAT fScaleY, FLOAT fRadian );
	
	//added by gmpbigsun: 회전축 변경 
	BOOL RenderTextureRotate( CPoint pt, CTexture* pTexture, DWORD dwBlendFactorAlhpa, FLOAT fRadian, BOOL bCenter, FLOAT fScaleX, FLOAT fScaleY );
	
	BOOL RenderTexture2( CPoint pt, CTexture* pTexture, FLOAT fScaleX = 1.0, FLOAT fScaleY = 1.0, D3DCOLOR coolor = 0xffffffff );
	BOOL RenderTextureEx2( CPoint pt, CPoint pt2, CTexture* pTexture, DWORD dwBlendFactorAlhpa, FLOAT fScaleX , FLOAT fScaleY, D3DCOLOR color );
	BOOL RenderTextureColor( CPoint pt, CTexture* pTexture, FLOAT fScaleX , FLOAT fScaleY, D3DCOLOR color );
		
	void SetTextColor( DWORD dwColor ) { m_dwTextColor = dwColor; }
	DWORD GetTextColor() { return m_dwTextColor; }
#ifdef __CLIENT
	void TextOut_EditString( int x,int y, CEditString& strEditString, int nPos = 0, int nLines = 0, int nLineSpace = 0 );
	void TextOut_EditString2( int x,int y, CEditString& strEditString, int nPos = 0, int nLines = 0, int nLineSpace = 0 );
	bool DrawTextMotion(std::string& MotionCmd, CPoint pt, CPoint pt2);
#endif
	void TextOut( int x,int y, LPCTSTR pszString, DWORD dwColor = 0xffffffff, DWORD dwShadowColor = 0x00000000 );
	void TextOut( int x,int y, int nValue, DWORD dwColor = 0xffffffff, DWORD dwShadowColor = 0x00000000 );
	void TextOut( int x,int y, FLOAT fXScale, FLOAT fYScale, LPCTSTR pszString, DWORD dwColor = 0xffffffff, DWORD dwShadowColor = 0x00000000 );

	HRESULT InitDeviceObjects( LPDIRECT3DDEVICE9 pd3dDevice );
	HRESULT RestoreDeviceObjects(  D3DSURFACE_DESC*  pd3dsdBackBuffer );
	HRESULT InvalidateDeviceObjects();
	HRESULT DeleteDeviceObjects();
};
class CTexture : public IDeviceRes
{
	BOOL m_bAutoFree;
public:
	SIZE  m_sizePitch;
	SIZE  m_size;
	FLOAT m_fuLT, m_fvLT;
	FLOAT m_fuRT, m_fvRT;
	FLOAT m_fuLB, m_fvLB;
	FLOAT m_fuRB, m_fvRB;
	POINT m_ptCenter;
	LPDIRECT3DTEXTURE9 m_pTexture;
#ifdef _DEBUG
	CString m_strFileName;
#endif
	
#ifdef __YDEBUG
	CString		m_strTexFileName;
	D3DCOLOR	m_d3dKeyColor;
	UINT		m_nLevels;
	BOOL		m_bMyLoader;
	DWORD		m_dwUsage;

	D3DPOOL		m_Pool;
	D3DFORMAT	m_Format;
#endif //__YDEBUG

	CTexture();
	~CTexture();

	void Invalidate();
	BOOL SetInvalidate(LPDIRECT3DDEVICE9 pd3dDevice);

	BOOL DeleteDeviceObjects();
	void SetAutoFree( BOOL bAuto ) { m_bAutoFree = bAuto; }


	LPDIRECT3DTEXTURE9 GetTexture() { return m_pTexture; }
	BOOL CreateTexture( LPDIRECT3DDEVICE9 pd3dDevice, int nWidth, int nHeight, 
						   UINT Levels, DWORD Usage, D3DFORMAT Format, D3DPOOL Pool = D3DPOOL_DEFAULT );
	BOOL LoadTexture( LPDIRECT3DDEVICE9 pd3dDevice, LPCTSTR pFileName, D3DCOLOR d3dKeyColor, BOOL bMyLoader = FALSE );
	//BOOL LoadTextureFromRes( LPDIRECT3DDEVICE9 pd3dDevice, LPCTSTR pFileName, D3DCOLOR d3dKeyColor, BOOL bMyLoader = FALSE );
	void Render( C2DRender* p2DRender, CPoint pt, DWORD dwBlendFactorAlhpa = 255 ) {
		p2DRender->RenderTexture( pt, this, dwBlendFactorAlhpa ); 
	}
	void Render( C2DRender* p2DRender, CPoint pt, CPoint pt2, DWORD dwBlendFactorAlhpa = 255, FLOAT fscalX = 1.0, FLOAT fscalY = 1.0 ) {
		p2DRender->RenderTextureEx( pt, pt2, this, dwBlendFactorAlhpa, fscalX, fscalY ); 
	}
	void RenderEx2( C2DRender* p2DRender, CPoint pt, CPoint pt2, DWORD dwBlendFactorAlhpa = 255, FLOAT fscalX = 1.0, FLOAT fscalY = 1.0, D3DCOLOR color = 0 ) {
		p2DRender->RenderTextureEx2( pt, pt2, this, dwBlendFactorAlhpa, fscalX, fscalY, color ); 
	}
	void RenderScal( C2DRender* p2DRender, CPoint pt, DWORD dwBlendFactorAlhpa = 255, FLOAT fscalX = 1.0, FLOAT fscalY = 1.0 ) {
		p2DRender->RenderTexture( pt, this, dwBlendFactorAlhpa , fscalX, fscalY ); 
	}
	void RenderRotate( C2DRender* p2DRender, CPoint pt, FLOAT fRadian, DWORD dwBlendFactorAlhpa = 255, FLOAT fscalX = 1.0, FLOAT fscalY = 1.0 ) {
		p2DRender->RenderTextureRotate( pt, this, dwBlendFactorAlhpa , fscalX, fscalY, fRadian ); 
	}

	//added by gmpbigsun : 회전축 변경가능 ( center or start point )
	void RenderRotate( C2DRender* p2DRender, CPoint pt, FLOAT fRadian, BOOL bCenter, DWORD dwBlendFactorAlhpa = 255, FLOAT fscalX = 1.0, FLOAT fscalY = 1.0 ) {
		p2DRender->RenderTextureRotate( pt, this, dwBlendFactorAlhpa, fRadian, bCenter, fscalX, fscalY ); 
	}
	
	void Render2( C2DRender* p2DRender, CPoint pt, D3DCOLOR color, float fscalX = 1.0f, float fscalY = 1.0f ) {
		p2DRender->RenderTexture2( pt, this, fscalX, fscalY, color ); 
	}
	void RenderScal2( C2DRender* p2DRender, CPoint pt, DWORD dwBlendFactorAlhpa = 255, FLOAT fscalX = 1.0, FLOAT fscalY = 1.0, D3DCOLOR color = 0 ) {
		p2DRender->RenderTextureColor( pt, this, fscalX, fscalY, color ); 
	}
	
	//CSize ComputeSize( CSize size );
};
//class CTextureMotion
//{
//public:
//	DWORD m_dwNumber;
//	CSize m_size;
//	LPDIRECT3DTEXTURE9 m_pTexture;
//	CTexture* m_ap2DTexture;
//
//	BOOL LoadScript( LPDIRECT3DDEVICE9 pd3dDevice, LPCTSTR pszFileName )
//	{
//		CScanner scanner;
//		if( scanner.Load( pszFileName ) == FALSE )
//		{
//			Error( "%s not found", pszFileName );
//			return FALSE;
//		}
//
//		DWORD dwCount = 0;
//		CTexture* pTexture;
//		BOOL bMultiLang = FALSE;
//
//		do {
//			scanner.GetToken();
//			if(scanner.Token == "number")
//			{	
//				m_dwNumber = scanner.GetNumber();
//				m_ap2DTexture = new CTexture[ m_dwNumber ];
//			}
//			else
//				if( scanner.Token == "MULTI_LANGUAGE" )
//				{
//					bMultiLang = TRUE;
//				}
//				else
//					if(scanner.Token == "texture")
//					{	
//						scanner.GetToken();	
//
//						TCHAR strFileName[MAX_PATH]; 
//						strcpy(strFileName,scanner.token);	
//						D3DCOLOR d3dKeyColor = scanner.GetHex();
//						// 여기서 텍스춰 생성 (Create the texture using D3DX)
//						D3DXIMAGE_INFO imageInfo;
//
//						if( bMultiLang )
//						{
//							LoadTextureFromRes( pd3dDevice, MakePath( "Theme\\", ::GetLanguage(), strFileName ), 
//								D3DX_DEFAULT, D3DX_DEFAULT, D3DX_DEFAULT, 0, D3DFMT_UNKNOWN, //D3DFMT_A4R4G4B4, 
//								D3DPOOL_MANAGED, D3DX_FILTER_TRIANGLE|D3DX_FILTER_MIRROR, 
//								D3DX_FILTER_TRIANGLE|D3DX_FILTER_MIRROR, d3dKeyColor, &imageInfo, NULL, &m_pTexture );
//						}
//						else
//						{
//							LoadTextureFromRes( pd3dDevice, strFileName, 
//								D3DX_DEFAULT, D3DX_DEFAULT, D3DX_DEFAULT, 0, D3DFMT_UNKNOWN, //D3DFMT_A4R4G4B4, 
//								D3DPOOL_MANAGED, D3DX_FILTER_TRIANGLE|D3DX_FILTER_MIRROR, 
//								D3DX_FILTER_TRIANGLE|D3DX_FILTER_MIRROR, d3dKeyColor, &imageInfo, NULL, &m_pTexture );
//						}
//
//						m_size.cx = imageInfo.Width;
//						m_size.cy = imageInfo.Height;
//					}
//					else
//						if(scanner.Token == "data") // 좌표와 사이즈 
//						{	
//							if( dwCount >= m_dwNumber )
//							{
//							}
//							pTexture = &m_ap2DTexture[ dwCount++ ];
//							pTexture->m_size.cx = scanner.GetNumber();	
//							pTexture->m_size.cy = scanner.GetNumber();	
//							pTexture->m_fuLT = (FLOAT)scanner.GetNumber() / m_size.cx;
//							pTexture->m_fvLT = (FLOAT)scanner.GetNumber() / m_size.cy;
//							pTexture->m_fuRT = (FLOAT)scanner.GetNumber() / m_size.cx;
//							pTexture->m_fvRT = (FLOAT)scanner.GetNumber() / m_size.cy;
//							pTexture->m_fuLB = (FLOAT)scanner.GetNumber() / m_size.cx;
//							pTexture->m_fvLB = (FLOAT)scanner.GetNumber() / m_size.cy;
//							pTexture->m_fuRB = (FLOAT)scanner.GetNumber() / m_size.cx;
//							pTexture->m_fvRB = (FLOAT)scanner.GetNumber() / m_size.cy;
//							pTexture->m_pTexture = m_pTexture;
//						}
//						else
//							if( scanner.Token == "pos" ) // 좌표
//							{	
//								if( dwCount >= m_dwNumber )
//								{
//								}
//								pTexture = &m_ap2DTexture[ dwCount++ ];
//								pTexture->m_size.cx = scanner.GetNumber();	
//								pTexture->m_size.cy = scanner.GetNumber();	
//								int x = scanner.GetNumber();
//								int y = scanner.GetNumber();
//								scanner.GetToken();
//								if( scanner.Token == "h" ) 
//								{
//									pTexture->m_fuRT = (FLOAT) x / m_size.cx;
//									pTexture->m_fvRT = (FLOAT) y / m_size.cy;
//									pTexture->m_fuLT = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//									pTexture->m_fvLT = (FLOAT) y / m_size.cy;
//									pTexture->m_fuRB = (FLOAT) x / m_size.cx;
//									pTexture->m_fvRB = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//									pTexture->m_fuLB = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//									pTexture->m_fvLB = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//								}
//								else
//									if( scanner.Token == "v" ) 
//									{
//										pTexture->m_fuLB = (FLOAT) x / m_size.cx;
//										pTexture->m_fvLB = (FLOAT) y / m_size.cy;
//										pTexture->m_fuRB = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//										pTexture->m_fvRB = (FLOAT) y / m_size.cy;
//										pTexture->m_fuLT = (FLOAT) x / m_size.cx;
//										pTexture->m_fvLT = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//										pTexture->m_fuRT = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//										pTexture->m_fvRT = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//									}
//									else
//										if( scanner.Token == "hv" )	
//										{
//											pTexture->m_fuRB = (FLOAT) x / m_size.cx;
//											pTexture->m_fvRB = (FLOAT) y / m_size.cy;
//											pTexture->m_fuLB = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//											pTexture->m_fvLB = (FLOAT) y / m_size.cy;
//											pTexture->m_fuRT = (FLOAT) x / m_size.cx;
//											pTexture->m_fvRT = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//											pTexture->m_fuLT = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//											pTexture->m_fvLT = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//										}
//										else
//										{
//											pTexture->m_fuLT = (FLOAT) x / m_size.cx;
//											pTexture->m_fvLT = (FLOAT) y / m_size.cy;
//											pTexture->m_fuRT = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//											pTexture->m_fvRT = (FLOAT) y / m_size.cy;
//											pTexture->m_fuLB = (FLOAT) x / m_size.cx;
//											pTexture->m_fvLB = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//											pTexture->m_fuRB = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//											pTexture->m_fvRB = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//										}
//										pTexture->m_pTexture = m_pTexture;
//							}
//							else
//								if(scanner.Token == "datauv") // uv 상태로 입력 
//								{	
//									if( dwCount >= m_dwNumber )
//									{   
//									}
//									pTexture = &m_ap2DTexture[ dwCount++ ];
//									pTexture->m_size.cx = scanner.GetNumber();	
//									pTexture->m_size.cy = scanner.GetNumber();	
//									pTexture->m_fuLT = scanner.GetFloat();
//									pTexture->m_fvLT = scanner.GetFloat();
//									pTexture->m_fuRT = scanner.GetFloat();
//									pTexture->m_fvRT = scanner.GetFloat();
//									pTexture->m_fuLB = scanner.GetFloat();
//									pTexture->m_fvLB = scanner.GetFloat();
//									pTexture->m_fuRB = scanner.GetFloat();
//									pTexture->m_fvRB = scanner.GetFloat();
//									pTexture->m_pTexture = m_pTexture;
//								}
//								else
//									if(scanner.Token == "serialize")
//									{	
//										if( dwCount >= m_dwNumber )
//										{
//											Error( "%s 에러, 할당 :%d, 실제갯수 : %d", pszFileName, m_dwNumber, dwCount );
//											return FALSE;
//										}
//										int nCnt = 0;
//										int nFrame = scanner.GetNumber();	
//										SIZE size;
//										size.cx = scanner.GetNumber();	
//										size.cy = scanner.GetNumber();	
//										POINT start;
//										start.x = scanner.GetNumber();	
//										start.y = scanner.GetNumber();	
//										POINT center;
//										center.x = scanner.GetNumber();	
//										center.y = scanner.GetNumber();	
//
//										int i; for( i = start.y; i < m_size.cy; i += size.cy )
//										{
//											int j; for(  j = start.x; j < m_size.cx; j += size.cx, nCnt++ )
//											{
//												if( nCnt < nFrame )
//												{
//
//													if( dwCount >= m_dwNumber )
//													{
//														Error( "%s 에러, 할당 :%d, 실제갯수 : %d", pszFileName, m_dwNumber, dwCount );
//														return FALSE;
//													}
//
//													pTexture = &m_ap2DTexture[ dwCount ];
//													dwCount++;
//
//													pTexture->m_size = size;	
//													pTexture->m_ptCenter = center;
//													int x = j;
//													int y = i;
//													pTexture->m_fuLT = (FLOAT) x / m_size.cx;
//													pTexture->m_fvLT = (FLOAT) y / m_size.cy;
//													pTexture->m_fuRT = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//													pTexture->m_fvRT = (FLOAT) y / m_size.cy;
//													pTexture->m_fuLB = (FLOAT) x / m_size.cx;
//													pTexture->m_fvLB = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//													pTexture->m_fuRB = (FLOAT) ( (FLOAT)x + pTexture->m_size.cx - 0 ) / (FLOAT)m_size.cx;
//													pTexture->m_fvRB = (FLOAT) ( (FLOAT)y + pTexture->m_size.cy - 0 ) / (FLOAT)m_size.cy;
//													pTexture->m_pTexture = m_pTexture;
//												}
//											}
//										}
//									}
//		} while(scanner.tok!=FINISHED);
//		return TRUE;
//	}
//
//
//};

class CTexturePack
{
public:
	DWORD m_dwNumber;
	CSize m_size;
	LPDIRECT3DTEXTURE9 m_pTexture;
	CTexture* m_ap2DTexture;
 
	CTexturePack();
	~CTexturePack();

	HRESULT		RestoreDeviceObjects(LPDIRECT3DDEVICE9 pd3dDevice);
	HRESULT		InvalidateDeviceObjects();

	BOOL DeleteDeviceObjects();
	DWORD GetNumber() { return m_dwNumber; }
	void MakeVertex( C2DRender* p2DRender, CPoint point, int nIndex, TEXTUREVERTEX** ppVertices );
	void MakeVertex( C2DRender* p2DRender, CPoint point, int nIndex, TEXTUREVERTEX2** ppVertices, DWORD dwColor );
	void Render( LPDIRECT3DDEVICE9 pd3dDevice, TEXTUREVERTEX* pVertices, int nVertexNum );
	void Render( LPDIRECT3DDEVICE9 pd3dDevice, TEXTUREVERTEX2* pVertices, int nVertexNum );

#if __VER >= 13 // __CSC_VER13_1
	virtual BOOL LoadScript( LPDIRECT3DDEVICE9 pd3dDevice, LPCTSTR pFileName );
#else //__CSC_VER13_1
	BOOL LoadScript( LPDIRECT3DDEVICE9 pd3dDevice, LPCTSTR pFileName );
#endif //__CSC_VER13_1

	CTexture* LoadTexture( LPDIRECT3DDEVICE9 pd3dDevice, LPCTSTR pFileName, D3DCOLOR d3dKeyColor );
	CTexture* GetAt( DWORD dwIndex ) {
		return &m_ap2DTexture[ dwIndex ];
	}
	void Render( C2DRender* p2DRender, CPoint pt, DWORD dwIndex, DWORD dwBlendFactorAlhpa = 255, FLOAT fScaleX=1.0f , FLOAT fScaleY=1.0f ) 
	{
		if( ((int)dwIndex >= (int)m_dwNumber) || (int)dwIndex < 0 )
		{
			LPCTSTR szErr = Error( "CTexturePack::Render : 범위를 벗어남 %d", (int)dwIndex );
			ADDERRORMSG( szErr );
			int *p = NULL;
			*p = 1;
		}
		p2DRender->RenderTexture( pt, &m_ap2DTexture[ dwIndex ], dwBlendFactorAlhpa, fScaleX , fScaleY ); 
	}
};
typedef map< string, CTexture* > CMapTexture;
typedef CMapTexture::value_type MapTexType;
typedef CMapTexture::iterator MapTexItor;

class CTextureMng
{
public:
	BOOL SetInvalidate(LPDIRECT3DDEVICE9 pd3dDevice);
	void Invalidate();
	CMapTexture m_mapTexture;
	//CMapStringToPtr m_mapTexture;
	CTextureMng();
	~CTextureMng();
	BOOL RemoveTexture( LPCTSTR pKey );
	BOOL DeleteDeviceObjects();
	CTexture* AddTexture( LPDIRECT3DDEVICE9 pd3dDevice, LPCTSTR pFileName, D3DCOLOR d3dKeyColor, BOOL bMyLoader = FALSE );
	CTexture* AddTexture( LPDIRECT3DDEVICE9 pd3dDevice, LPCTSTR pKey, CTexture* pTexture );
	CTexture* GetAt( LPCTSTR pFileName );
};
#ifdef __CLIENT
// 몹, 플레이어 데미지 출력
class CDamageNum
{
public:
	DWORD m_nFrame;
	DWORD m_nNumber;
	DWORD m_nAttribute;
	D3DXVECTOR3 m_vPos;
	FLOAT	m_fY, m_fDy;
	int		m_nState;
	int		m_nCnt;

	CDamageNum(D3DXVECTOR3 vPos,DWORD nNumber,DWORD nAttribute) 
	{ m_nFrame=0; m_nNumber=nNumber; m_vPos=vPos; m_nAttribute=nAttribute; m_nState = 0; m_nCnt = 0; }
	~CDamageNum() {};

	void Process();
	void Render(CTexturePack *textPackNum);
#ifdef __CLIENT
#ifndef __VM_0820
#ifndef __MEM_TRACE
	static MemPooler<CDamageNum>*	m_pPool;
	void*	operator new( size_t nSize )	{	return CDamageNum::m_pPool->Alloc();	}
	void*	operator new( size_t nSize, LPCSTR lpszFileName, int nLine )	{	return CDamageNum::m_pPool->Alloc();	}
	void	operator delete( void* lpMem )	{	CDamageNum::m_pPool->Free( (CDamageNum*)lpMem );	}
	void	operator delete( void* lpMem, LPCSTR lpszFileName, int nLine )	{	CDamageNum::m_pPool->Free( (CDamageNum*)lpMem );	}
#endif	// __MEM_TRACE
#endif	// __VM_0820
#endif	// __CLIENT
};

// 데미지 숫자 관리자
class CDamageNumMng
{
public:
	CPtrArray m_Array;
	D3DXMATRIX m_matProj,m_matView,m_matWorld;
	D3DVIEWPORT9 m_viewport;
	CTexturePack m_textPackNum;

	CDamageNumMng() { D3DXMatrixIdentity(&m_matWorld); };
	~CDamageNumMng();

	HRESULT		RestoreDeviceObjects();
	HRESULT		InvalidateDeviceObjects();

	BOOL DeleteDeviceObjects();
	void LoadTexture(LPDIRECT3DDEVICE9 pd3dDevice);
	void AddNumber(D3DXVECTOR3 vPos,DWORD nNumber,DWORD nAttribute); // 새로운 데미지 표시를 생성시킨다.
	void Process(); // 현재 생성된 데미지 표시들을 처리한다.
	void Render(); // 현재 생성된 데미지 표시들을 출력한다.
};
#endif
#endif

