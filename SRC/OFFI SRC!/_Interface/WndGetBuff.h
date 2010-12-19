#if __VER >= 13 // __HOUSING
#ifndef __WNDGETBUFF__H
#define __WNDGETBUFF__H

class CWndGetBuff : public CWndNeuz 
{ 
public: 
	CWndGetBuff(); 
	virtual ~CWndGetBuff(); 

	virtual BOOL Initialize( CWndBase* pWndParent = NULL, DWORD nType = MB_OK ); 
	virtual BOOL OnChildNotify( UINT message, UINT nID, LRESULT* pLResult ); 
	virtual void OnDraw( C2DRender* p2DRender ); 
	virtual	void OnInitialUpdate(); 
	virtual BOOL OnCommand( UINT nID, DWORD dwMessage, CWndBase* pWndBase ); 
	virtual void OnSize( UINT nType, int cx, int cy ); 
	virtual void OnLButtonUp( UINT nFlags, CPoint point ); 
	virtual void OnLButtonDown( UINT nFlags, CPoint point ); 

	void SetVar(TCHAR * key);
public:
	TCHAR	m_szCharacterKey[32];
}; 

class CWndGetBuff2 : public CWndGetBuff 
{ 
public: 
	virtual BOOL Initialize( CWndBase* pWndParent = NULL, DWORD nType = MB_OK ); 
}; 

#endif
#endif // __HOUSING