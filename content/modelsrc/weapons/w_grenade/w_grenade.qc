// Created by Crowbar 0.27.0.0

$ModelName "weapons/w_grenade.mdl"

$StaticProp

$BodyGroup "studio"
{
	studio "w_grenade_reference.smd"
}

$texturegroup "<name>"
{
    { "w_grenadesheet" }
    { "w_grenadesheet_blue" }
}

$SurfaceProp "grenade"

$Contents "solid"

$MaxEyeDeflection 90

$CDMaterials "models\weapons\w_grenade\"

$Attachment "fuse" "static_prop" 0 0 4.5 rotate 0 90 0

$CBox 0 0 0 0 0 0

$BBox -2.089 -2.089 -4.684 2.089 2.089 4.839


$Sequence "idle" {
	"w_grenade_anims\idle.smd"
	activity "ACT_VM_IDLE" 1
	fadein 0.2
	fadeout 0.2
	fps 30
}

$CollisionModel "w_grenade_physics.smd"
{
	$mass 1
	$inertia 1
	$damping 0
	$rotdamping 0

}
