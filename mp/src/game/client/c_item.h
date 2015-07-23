#ifndef C_ITEM_H
#define C_ITEM_H

#ifdef _WIN32
#pragma once
#endif

#include "c_baseanimating.h"

class C_Item : public C_BaseAnimating
{
public:
	DECLARE_CLASS( C_Item, C_BaseAnimating );
	DECLARE_CLIENTCLASS();
};

#endif // C_ITEM_H